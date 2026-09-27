"""Report electrical pad proximity from the read-only extracted board manifest."""

import json
import math
from pathlib import Path


manifest = json.loads(Path(__file__).with_name("placement_manifest.json").read_text())
parts = {p["ref"]: p for p in manifest["components"]}
results = []
for constraint in manifest["constraints"]:
    if constraint["type"] != "pad_proximity":
        continue
    part = parts[constraint["ref"]]
    anchor = parts[constraint["anchor_ref"]]
    pad = next(p for p in part["pads"] if p["number"] == constraint["pad"])
    anchor_pad = next(p for p in anchor["pads"] if p["number"] == constraint["anchor_pad"])
    distance = math.dist((pad["x"], pad["y"]), (anchor_pad["x"], anchor_pad["y"]))
    results.append({
        "ref": constraint["ref"], "pad": constraint["pad"],
        "anchor": constraint["anchor_ref"], "anchor_pad": constraint["anchor_pad"],
        "distance": round(distance, 2), "maximum": constraint["maximum"],
        "excess": round(distance - constraint["maximum"], 2),
    })

violations = [r for r in results if r["excess"] > 0]
print(f"Electrical pad constraints: {len(results)}; above maximum: {len(violations)}")
for result in sorted(violations, key=lambda r: r["excess"], reverse=True):
    print("{ref}.{pad} to {anchor}.{anchor_pad}: {distance:.2f} mm > {maximum:.2f} mm (+{excess:.2f})".format(**result))
