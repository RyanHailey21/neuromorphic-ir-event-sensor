"""Remove only KiCad DRC identified dangling vias through Companion MCP."""

import json
import sys
from pathlib import Path

import pcbnew


board_path = Path(sys.argv[1]).resolve()
report_path = Path(sys.argv[2]).resolve()
report = json.loads(report_path.read_text(encoding="utf-8"))
targets = {
    item["uuid"]
    for violation in report["violations"]
    if violation["type"] == "via_dangling"
    for item in violation["items"]
    if item["description"].startswith("Via ")
}
if not targets:
    raise RuntimeError("No dangling via UUIDs found in DRC report")

board = pcbnew.LoadBoard(str(board_path))
matches = [track for track in board.GetTracks()
           if isinstance(track, pcbnew.PCB_VIA)
           and track.m_Uuid.AsString() in targets]
if len(matches) != len(targets):
    raise RuntimeError(f"Report named {len(targets)} vias but board matched {len(matches)}")
for via in matches:
    board.Remove(via)
pcbnew.SaveBoard(str(board_path), board)
print(f"Removed {len(matches)} DRC identified dangling vias")
