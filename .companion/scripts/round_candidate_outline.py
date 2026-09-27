"""Round the 50 x 70 mm candidate's corners through Companion's KiCad Python.

Invoked only by the KiCad Companion execute_project_script MCP tool.
"""

import math
import sys
from pathlib import Path

import pcbnew


board_path = Path(sys.argv[1]).resolve()
radius = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
board = pcbnew.LoadBoard(str(board_path))
edges = [shape for shape in board.GetDrawings()
         if isinstance(shape, pcbnew.PCB_SHAPE)
         and shape.GetLayer() == pcbnew.Edge_Cuts]
if not ((len(edges) == 1 and edges[0].GetShape() == pcbnew.S_RECT)
        or (len(edges) == 4 and all(shape.GetShape() == pcbnew.S_SEGMENT for shape in edges))):
    raise RuntimeError(f"Expected one rectangle or four straight Edge.Cuts segments, found {len(edges)}")

if len(edges) == 1:
    start, end = edges[0].GetStart(), edges[0].GetEnd()
    x0, y0 = start.x / 1e6, start.y / 1e6
    x1, y1 = end.x / 1e6, end.y / 1e6
else:
    box = board.GetBoardEdgesBoundingBox()
    x0, y0 = box.GetX() / 1e6 + 0.025, box.GetY() / 1e6 + 0.025
    x1, y1 = box.GetRight() / 1e6 - 0.025, box.GetBottom() / 1e6 - 0.025
if not (abs(x1 - x0 - 50) < 0.1 and abs(y1 - y0 - 70) < 0.1):
    raise RuntimeError(f"Unexpected board dimensions {(x0, y0, x1, y1)}")
if radius <= 0 or radius > 5:
    raise ValueError("Corner radius must be in (0, 5] mm")

for edge in edges:
    board.Remove(edge)


def point(x, y):
    return pcbnew.VECTOR2I(round(x * 1e6), round(y * 1e6))


def segment(start, end):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.S_SEGMENT)
    shape.SetStart(point(*start))
    shape.SetEnd(point(*end))
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(50000)
    board.Add(shape)


def arc(start, middle, end):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.S_ARC)
    shape.SetArcGeometry(point(*start), point(*middle), point(*end))
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(50000)
    board.Add(shape)


r = radius
d = r / math.sqrt(2)
segment((x0+r, y0), (x1-r, y0))
arc((x1-r, y0), (x1-r+d, y0+r-d), (x1, y0+r))
segment((x1, y0+r), (x1, y1-r))
arc((x1, y1-r), (x1-r+d, y1-r+d), (x1-r, y1))
segment((x1-r, y1), (x0+r, y1))
arc((x0+r, y1), (x0+r-d, y1-r+d), (x0, y1-r))
segment((x0, y1-r), (x0, y0+r))
arc((x0, y0+r), (x0+r-d, y0+r-d), (x0+r, y0))

pcbnew.SaveBoard(str(board_path), board)
print(f"Rounded {board_path.name}: {x1-x0:.1f} x {y1-y0:.1f} mm, R{radius:.1f} mm")
