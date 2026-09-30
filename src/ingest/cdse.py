"""Copernicus Data Space (CDSE) access: Sentinel-1 search + same-track pairing."""
import os, requests
from datetime import datetime, timedelta

CATALOGUE = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
TOKEN_URL = ("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
             "protocol/openid-connect/token")

def get_token(user=None, password=None):
    user = user or os.environ["CDSE_USER"]
    password = password or os.environ["CDSE_PASS"]
    r = requests.post(TOKEN_URL, data={
        "client_id": "cdse-public", "grant_type": "password",
        "username": user, "password": password}, timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]

def _attr(product, name):
    for a in product.get("Attributes", []):
        if a["Name"] == name:
            return a["Value"]
    return None

def search_s1(bbox, start, end, product_type="IW_GRDH_1S"):
    """bbox=[minlon,minlat,maxlon,maxlat]; start/end 'YYYY-MM-DD'."""
    x0, y0, x1, y1 = bbox
    poly = f"POLYGON(({x0} {y0},{x1} {y0},{x1} {y1},{x0} {y1},{x0} {y0}))"
    flt = (
        "Collection/Name eq 'SENTINEL-1' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{poly}') "
        f"and ContentDate/Start gt {start}T00:00:00.000Z "
        f"and ContentDate/Start lt {end}T23:59:59.999Z "
        "and Attributes/OData.CSC.StringAttribute/any(a:a/Name eq 'productType' "
        f"and a/OData.CSC.StringAttribute/Value eq '{product_type}')"
    )
    params = {"$filter": flt, "$expand": "Attributes",
              "$orderby": "ContentDate/Start asc", "$top": 200}
    r = requests.get(CATALOGUE, params=params, timeout=120)
    r.raise_for_status()
    out = []
    for p in r.json().get("value", []):
        out.append({
            "id": p["Id"], "name": p["Name"],
            "start": p["ContentDate"]["Start"],
            "size_mb": round(p.get("ContentLength", 0) / 1e6),
            "rel_orbit": _attr(p, "relativeOrbitNumber"),
            "direction": _attr(p, "orbitDirection"),
            "platform": _attr(p, "platformSerialIdentifier"),
        })
    return out

def find_same_track_pairs(products, flood_date):
    """For each (rel_orbit, direction): latest scene before the flood date and
    earliest scene on/after it. Reports the gap in days (12 is ideal;
    multiples of 6 are still same-geometry)."""
    fd = datetime.strptime(flood_date, "%Y-%m-%d")
    groups = {}
    for p in products:
        groups.setdefault((p["rel_orbit"], p["direction"]), []).append(p)
    pairs = []
    for (orb, d), items in groups.items():
        pre = [p for p in items if datetime.fromisoformat(p["start"][:19]) < fd]
        post = [p for p in items if datetime.fromisoformat(p["start"][:19]) >= fd]
        if pre and post:
            a = max(pre, key=lambda p: p["start"])
            b = min(post, key=lambda p: p["start"])
            gap = (datetime.fromisoformat(b["start"][:19])
                   - datetime.fromisoformat(a["start"][:19])).days
            pairs.append({"rel_orbit": orb, "direction": d, "gap_days": gap,
                          "pre": a, "post": b})
    return sorted(pairs, key=lambda x: abs(x["gap_days"] - 12))

def download(product_id, name, token, out_dir="/kaggle/temp"):
    os.makedirs(out_dir, exist_ok=True)
    url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    path = os.path.join(out_dir, name.replace(".SAFE", "") + ".zip")
    with requests.get(url, headers={"Authorization": f"Bearer {token}"},
                      stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return path
