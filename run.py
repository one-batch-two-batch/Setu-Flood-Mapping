"""Setu Flood Mapping: end-to-end pipeline.
Usage: python run.py --aoi 85.0,28.0,85.4,28.4 --date 2026-08-26
"""
import argparse, json, os

def parse_aoi(s):
    if os.path.isfile(s):
        return json.load(open(s))          # GeoJSON file
    minx, miny, maxx, maxy = map(float, s.split(","))
    return {"bbox": [minx, miny, maxx, maxy]}

def stage(name):
    print(f"[stage] {name}: not implemented yet")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--aoi", required=True, help="minlon,minlat,maxlon,maxlat or a GeoJSON path")
    p.add_argument("--date", required=True, help="flood date, YYYY-MM-DD")
    p.add_argument("--out", default="outputs")
    a = p.parse_args()
    aoi = parse_aoi(a.aoi)
    os.makedirs(a.out, exist_ok=True)
    print("AOI:", aoi, "| flood date:", a.date)
    for s in ["ingest", "radar change detection", "optical", "segmentation",
              "damage assessment", "cut-off analysis", "hydrology (bonus)",
              "dashboard", "situation report"]:
        stage(s)

if __name__ == "__main__":
    main()
