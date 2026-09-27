"""Match Vishay top-view polarity and start autorouting with no old copper."""

import shutil
import sys
from pathlib import Path

import pcbnew


board_path = Path(sys.argv[1]).resolve()
library_path = Path(sys.argv[2]).resolve()
board = pcbnew.LoadBoard(str(board_path))
library = pcbnew.FootprintLoad(str(library_path), "XDCR_VBPW34S")
if library is None:
    raise RuntimeError("VBPW34S footprint library did not load")


def correct(footprint):
    pads = {pad.GetNumber(): pad for pad in footprint.Pads()}
    if set(pads) != {"A", "K"}:
        raise RuntimeError("Unexpected VBPW34S pads")
    left = pcbnew.FromMM(-3.575)
    right = pcbnew.FromMM(3.575)
    if pads["K"].GetFPRelativePosition().x == right and pads["A"].GetFPRelativePosition().x == left:
        return
    if pads["K"].GetFPRelativePosition().x != left or pads["A"].GetFPRelativePosition().x != right:
        raise RuntimeError("Footprint polarity no longer matches expected source")
    pads["K"].SetFPRelativePosition(pcbnew.VECTOR2I(right, 0))
    pads["A"].SetFPRelativePosition(pcbnew.VECTOR2I(left, 0))
    circles = [item for item in footprint.GraphicalItems()
               if isinstance(item, pcbnew.PCB_SHAPE)
               and item.GetShape() == pcbnew.SHAPE_T_CIRCLE]
    if len(circles) != 2:
        raise RuntimeError(f"Expected two polarity marker circles, got {len(circles)}")
    origin = footprint.GetPosition()
    for item in circles:
        start, end = item.GetStart(), item.GetEnd()
        item.SetStart(pcbnew.VECTOR2I(2 * origin.x - start.x, 2 * origin.y - start.y))
        item.SetEnd(pcbnew.VECTOR2I(2 * origin.x - end.x, 2 * origin.y - end.y))


refs = {"D1", "D2", "D3", "D4"}
footprints = [fp for fp in board.GetFootprints() if fp.GetReference() in refs]
if {fp.GetReference() for fp in footprints} != refs:
    raise RuntimeError("Missing photodiode footprint")

backup = board_path.with_suffix(".before_polarity_fix.kicad_pcb")
shutil.copy2(board_path, backup)
for fp in footprints:
    correct(fp)
correct(library)
pcbnew.FootprintSave(str(library_path), library)
saved_library = pcbnew.FootprintLoad(str(library_path), "XDCR_VBPW34S")
saved_pads = {pad.GetNumber(): pad for pad in saved_library.Pads()}
if saved_pads["K"].GetFPRelativePosition().x != pcbnew.FromMM(3.575):
    raise RuntimeError("Failed to save corrected library footprint")

previous = list(board.GetTracks())
for track in previous:
    board.Remove(track)
pcbnew.SaveBoard(str(board_path), board)
check = pcbnew.LoadBoard(str(board_path))
if len(list(check.GetTracks())) != 0:
    raise RuntimeError("Routing reset failed: tracks or vias remain")
print(f"Corrected four photodiode footprints and library; removed {len(previous)} tracks/vias; verified zero remain")
