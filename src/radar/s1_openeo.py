"""Terrain-corrected Sentinel-1 (VV, VH in dB) via CDSE openEO."""
import os
from datetime import datetime, timedelta
import openeo

def connect():
    return openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

def s1_cube(conn, bbox, date):
    """One acquisition date -> sigma0 (terrain corrected) in dB, VV+VH."""
    d0 = datetime.strptime(date, "%Y-%m-%d")
    d1 = d0 + timedelta(days=1)
    cube = conn.load_collection(
        "SENTINEL1_GRD",
        spatial_extent={"west": bbox[0], "south": bbox[1],
                        "east": bbox[2], "north": bbox[3]},
        temporal_extent=[d0.strftime("%Y-%m-%d"), d1.strftime("%Y-%m-%d")],
        bands=["VV", "VH"],
    )
    cube = cube.sar_backscatter(coefficient="sigma0-ellipsoid",
                                elevation_model="COPERNICUS_30")
    cube = cube.apply(lambda x: 10 * x.log(base=10))      # linear -> dB
    return cube.reduce_dimension(dimension="t", reducer="mean")

def fetch(conn, bbox, date, out_path):
    """Runs a batch job and downloads a GeoTIFF."""
    cube = s1_cube(conn, bbox, date)
    job = cube.save_result("GTiff").create_job(title=f"S1 {date}")
    job.start_and_wait()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    job.get_results().download_file(out_path)
    return out_path
