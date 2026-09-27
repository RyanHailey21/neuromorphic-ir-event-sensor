"""Fast pad-aware placement planner; emits JSON and never saves a KiCad board.

Fixed optical, mechanical, connector, and IC anchors are preserved. Parts with
electrical constraints are placed first against pad distances and courtyard
boxes. Unconstrained parts use the remaining free space.
"""

import json
import math
from pathlib import Path


root = Path(__file__).parent
data = json.loads((root / "placement_manifest.json").read_text())
parts = {item["ref"]: item for item in data["components"]}
constraints = data["constraints"]
by_ref = {}
for item in constraints:
    by_ref.setdefault(item["ref"], []).append(item)

fixed = {ref for ref, part in parts.items() if part["fixed"]}
fixed |= {ref for ref in parts if ref.startswith("U")}
fixed |= {"Q1"}
# Treat each temporal coupling capacitor and 22 kOhm return resistor as a
# local pair. These coordinates were checked against the mechanical anchors.
pair_positions = {
    "C5": (10.5, 11), "R5": (10.5, 13),
    "C6": (39.5, 11), "R6": (39.5, 13),
    "C7": (10.5, 23.5), "R7": (10.5, 25.5),
    "C8": (39.5, 23.5), "R8": (39.5, 25.5),
}
fixed.update(pair_positions)
placed = set(fixed)
outline = data["board"]["outline"]


def rotate(x, y, degrees):
    radians = math.radians(degrees)
    return (x * math.cos(radians) + y * math.sin(radians),
            -x * math.sin(radians) + y * math.cos(radians))


def pad_xy(part, number, x=None, y=None, angle=None):
    x = part["x"] if x is None else x
    y = part["y"] if y is None else y
    angle = part["rotation"] if angle is None else angle
    pad = next(p for p in part["pads"] if p["number"] == str(number))
    dx = pad["x"] - part["x"]
    dy = pad["y"] - part["y"]
    lx, ly = rotate(dx, dy, -part["rotation"])
    rx, ry = rotate(lx, ly, angle)
    return x + rx, y + ry


reference = parts["U17"]
new_x, new_y = 125.0, 103.5
new_pads = {pad["number"]: pad_xy(reference, pad["number"], new_x, new_y, 0)
            for pad in reference["pads"]}
for pad in reference["pads"]:
    pad["x"], pad["y"] = new_pads[pad["number"]]
reference["x"], reference["y"], reference["rotation"] = new_x, new_y, 0


for ref, (x, y) in pair_positions.items():
    part = parts[ref]
    new_x, new_y = x + 100, y + 100
    new_pads = {pad["number"]: pad_xy(part, pad["number"], new_x, new_y, 0)
                for pad in part["pads"]}
    for pad in part["pads"]:
        pad["x"], pad["y"] = new_pads[pad["number"]]
    part["x"], part["y"], part["rotation"] = new_x, new_y, 0


def bounds(part, x=None, y=None, angle=None):
    x = part["x"] if x is None else x
    y = part["y"] if y is None else y
    angle = part["rotation"] if angle is None else angle
    dx, dy = rotate(part["bbox_dx"], part["bbox_dy"], angle)
    w, h = part["width"], part["height"]
    if round(angle / 90) % 2:
        w, h = h, w
    return x + dx - w / 2, y + dy - h / 2, x + dx + w / 2, y + dy + h / 2


def free(part, x, y, angle, spacing=0.35):
    box = bounds(part, x, y, angle)
    if (box[0] < outline["min_x"] + 0.75 or box[1] < outline["min_y"] + 0.75
            or box[2] > outline["max_x"] - 0.75 or box[3] > outline["max_y"] - 0.75):
        return False
    for other_ref in placed:
        other = parts[other_ref]
        other_box = bounds(other)
        if (box[0] < other_box[2] + spacing and box[2] > other_box[0] - spacing
                and box[1] < other_box[3] + spacing and box[3] > other_box[1] - spacing):
            return False
    return True


def candidates(cx, cy, max_radius=12):
    # The Manhattan rings visit nearby legal grid points before remote ones.
    gx = round(cx * 2) / 2
    gy = round(cy * 2) / 2
    for radius in range(round(max_radius * 2) + 1):
        for ix in range(-radius, radius + 1):
            iy = radius - abs(ix)
            yield gx + ix * 0.5, gy + iy * 0.5
            if iy:
                yield gx + ix * 0.5, gy - iy * 0.5


def score(part, x, y, angle, items):
    total = 0.0
    for item in items:
        if item["anchor_ref"] not in placed:
            continue
        px, py = pad_xy(part, item["pad"], x, y, angle)
        qx, qy = pad_xy(parts[item["anchor_ref"]], item["anchor_pad"])
        distance = math.hypot(px - qx, py - qy)
        target = item["target"]
        maximum = item["maximum"]
        total += item["weight"] * max(0, distance - target) ** 2
        total += 100000 * max(0, distance - maximum) ** 2
    return total


def target_for(part, items):
    points = []
    for item in items:
        if item["anchor_ref"] in placed:
            points.append(pad_xy(parts[item["anchor_ref"]], item["anchor_pad"]))
    if points:
        return sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points)
    return part["x"], part["y"]


def place(ref):
    part = parts[ref]
    items = by_ref.get(ref, [])
    cx, cy = target_for(part, items)
    best = None
    # Evaluate only collision-free sites. This is far cheaper than rescoring
    # the entire 111-part board for every trial position.
    for x, y in candidates(cx, cy, 12 if items else 18):
        for angle in (0, 90, 180, 270):
            if not free(part, x, y, angle):
                continue
            value = score(part, x, y, angle, items)
            value += 0.05 * math.hypot(x - part["x"], y - part["y"])
            if best is None or value < best[0]:
                best = value, x, y, angle
        if best and items and best[0] < 0.01:
            break
        if best and not items:
            break
    if best is None:
        raise RuntimeError(f"No collision-free location found for {ref} near {(cx, cy)} with {len(placed)} placed")
    _, part["x"], part["y"], part["rotation"] = best
    placed.add(ref)


# Place anchors of other constrained parts before their dependents.
unplaced = {ref for ref in parts if ref not in placed}
while unplaced:
    ready = [ref for ref in unplaced if all(
        item["anchor_ref"] in placed for item in by_ref.get(ref, []))]
    if not ready:
        ready = list(unplaced)
    ready.sort(key=lambda ref: (
        0 if by_ref.get(ref) else 1,
        -max((item["weight"] for item in by_ref.get(ref, [])), default=0),
        -len(by_ref.get(ref, [])), ref))
    ref = ready[0]
    place(ref)
    unplaced.remove(ref)

fixed_centers = {}
for ref, part in parts.items():
    dx, dy = rotate(part["bbox_dx"], part["bbox_dy"], part["rotation"])
    fixed_centers[ref] = [round(part["x"] + dx - 100, 4),
                          round(part["y"] + dy - 100, 4),
                          int(part["rotation"])]

output = root / "placement_plan_fast.json"
output.write_text(json.dumps({"fixed": fixed_centers}, indent=2) + "\n")
print(f"Placed {len(parts)} components; wrote {output}")
