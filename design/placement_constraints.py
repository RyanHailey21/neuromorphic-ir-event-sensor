"""Electrical placement priorities for the Rev A candidate.

Writes optimizer inputs only. KiCad source mutation remains in Companion MCP.
"""

import json
from pathlib import Path


constraints = []


def pad(ref, pin, anchor, anchor_pin, target, maximum, weight=100, hard=True):
    constraints.append({
        "type": "pad_proximity", "ref": ref, "pad": str(pin),
        "anchor_ref": anchor, "anchor_pad": str(anchor_pin),
        "target": target, "maximum": maximum, "weight": weight, "hard": hard,
    })


for channel in range(1, 5):
    tia = f"U{channel}"
    diode = f"D{channel}"
    cmp = f"U{channel + 4}"
    feedback_r = f"R{channel}"
    feedback_c = f"C{channel}"
    adapt_c = f"C{channel + 4}"
    adapt_r = f"R{channel + 4}"
    tia_bypass = f"C{channel + 8}"
    cmp_bypass = f"C{channel + 12}"

    pad(tia, 2, diode, "K", 4, 8, 1000)
    pad(feedback_r, 1, tia, 2, 1.4, 3.5, 600)
    pad(feedback_r, 2, tia, 6, 1.4, 3.5, 600)
    pad(feedback_c, 1, tia, 2, 1.4, 3.5, 600)
    pad(feedback_c, 2, tia, 6, 1.4, 3.5, 600)
    pad(tia_bypass, 1, tia, 7, 1.2, 2.5, 900)
    pad(adapt_c, 1, tia, 6, 2.0, 5.0, 200)
    pad(adapt_c, 2, adapt_r, 1, 1.0, 2.5, 400)
    # Keep the adaptation resistor next to its coupling capacitor. The
    # comparator input is high impedance and can tolerate the longer run.
    pad(adapt_r, 1, tia, 6, 3.5, 6.0, 250)
    pad(cmp_bypass, 1, cmp, 8, 1.2, 2.5, 900)
    pad(f"R{39 + channel}", 2, cmp, 5, 1.5, 4.0, 250)
    pad(f"R{30 + 2 * channel}", 1, cmp, 1, 1.5, 4.0, 150)
    pad(f"R{31 + 2 * channel}", 1, cmp, 7, 1.5, 4.0, 150)

    for polarity_index in range(2):
        event_index = (channel - 1) * 2 + polarity_index + 1
        oneshot = f"U{8 + event_index}"
        timing_r = f"R{8 + event_index}"
        timing_c = f"C{16 + event_index}"
        output_r = f"R{16 + event_index}"
        bypass = f"C{29 + event_index}"
        pad(bypass, 1, oneshot, 8, 1.0, 2.5, 900)
        pad(timing_r, 2, oneshot, 7, 1.5, 4.0, 500)
        pad(timing_c, 1, oneshot, 6, 1.5, 4.0, 500)
        pad(timing_c, 2, oneshot, 7, 1.5, 4.0, 500)
        pad(output_r, 1, oneshot, 5, 1.5, 4.0, 300)

pad("C25", 1, "U17", 2, 1.2, 2.5, 800)
pad("C26", 1, "U17", 2, 1.2, 2.5, 800)
pad("R26", 2, "Q1", 1, 1.5, 4.0, 300)
pad("R27", 1, "Q1", 1, 1.5, 4.0, 300)
pad("R25", 2, "D5", 2, 3.0, 8.0, 200)

overlay = {
    "metadata": {"purpose": "Rev A electrically constrained PCB placement"},
    "fixed_refs": ["H1", "H2", "H3", "H4", "H5", "H6",
                   "J1", "J2", "J3", "D1", "D2", "D3", "D4", "D5"],
    "board": {"edge_clearance": 0.5, "grid": 0.25},
    "settings": {
        "iterations": 30000, "seed": 3,
        "default_net_weight": 1,
        "ignored_nets": ["/GND", "GND"],
        "component_spacing": 0.5,
        "component_spacing_weight": 50,
        "routing_crossing_weight": 25,
        "net_weights": {
            **{f"/TIA_IN_{q}": 100 for q in ("TL", "TR", "BL", "BR")},
            **{f"/VPHOTO_{q}": 40 for q in ("TL", "TR", "BL", "BR")},
            **{f"/VEVENT_{q}": 25 for q in ("TL", "TR", "BL", "BR")},
        },
    },
    "constraints": constraints,
}

path = Path(__file__).with_name("placement_overlay.json")
path.write_text(json.dumps(overlay, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(constraints)} electrical constraints to {path}")
