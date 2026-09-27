"""Leave placement and outline intact; remove routes and pours before Freerouting."""

import sys
from pathlib import Path
import pcbnew

board_path = Path(sys.argv[1]).resolve()
board = pcbnew.LoadBoard(str(board_path))
tracks = list(board.GetTracks())
zones = list(board.Zones())
if tracks:
    raise RuntimeError(f"Expected zero tracks/vias before fresh route, found {len(tracks)}")
for zone in zones:
    board.Remove(zone)
pcbnew.SaveBoard(str(board_path), board)
check = pcbnew.LoadBoard(str(board_path))
if len(list(check.GetTracks())) or len(list(check.Zones())):
    raise RuntimeError("The route input is not free of copper and zones")
print(f"Verified zero tracks/vias; removed {len(zones)} zones; verified zero zones")
