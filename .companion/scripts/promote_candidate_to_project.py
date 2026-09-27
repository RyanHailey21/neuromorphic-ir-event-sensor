"""Promote the verified headless KiCad candidate into the main project files."""

import hashlib
import shutil
import sys
from pathlib import Path

import pcbnew


root = Path(sys.argv[1]).resolve()
candidate = root / "headless_candidate"
stem = "neuromorphic-ir-event-sensor"
extensions = (".kicad_pcb", ".kicad_sch", ".kicad_pro")

if not (root / ".git").exists():
    raise RuntimeError("Expected version controlled project root for rollback")

source_board = pcbnew.LoadBoard(str(candidate / f"{stem}.kicad_pcb"))
if len(list(source_board.GetTracks())) < 1000 or len(list(source_board.Zones())) != 2:
    raise RuntimeError("Candidate does not have the expected final routing and pours")
for ref in ("D1", "D2", "D3", "D4"):
    fp = next(fp for fp in source_board.GetFootprints() if fp.GetReference() == ref)
    pads = {pad.GetNumber(): pad for pad in fp.Pads()}
    if pads["K"].GetFPRelativePosition().x != pcbnew.FromMM(3.575):
        raise RuntimeError(f"{ref} does not have corrected Vishay polarity")

for extension in extensions:
    source = candidate / f"{stem}{extension}"
    target = root / source.name
    if not source.is_file() or not target.is_file():
        raise RuntimeError(f"Missing KiCad project file: {source} or {target}")
    shutil.copy2(source, target)
    if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
        raise RuntimeError(f"Copy verification failed for {target.name}")

for table_name in ("fp-lib-table", "sym-lib-table"):
    text = (candidate / table_name).read_text(encoding="utf-8")
    if text.count("${KIPRJMOD}/../vendor/") != 1:
        raise RuntimeError(f"Unexpected path in {table_name}")
    (root / table_name).write_text(
        text.replace("${KIPRJMOD}/../vendor/", "${KIPRJMOD}/vendor/"),
        encoding="utf-8",
    )

loaded = pcbnew.LoadBoard(str(root / f"{stem}.kicad_pcb"))
print(
    f"Promoted project: {len(list(loaded.GetFootprints()))} footprints, "
    f"{len(list(loaded.GetTracks()))} tracks/vias, {len(list(loaded.Zones()))} zones"
)
