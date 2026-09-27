"""Import the user-provided VBPW34S vendor library through Companion MCP."""

import sys
import zipfile
from pathlib import Path

import pcbnew


root = Path(sys.argv[1]).resolve()
archive = (root / "VBPW34S.zip").resolve()
candidate = root / "headless_candidate"
vendor = root / "vendor"
pretty = vendor / "VBPW34S.pretty"
pretty.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(archive) as bundle:
    expected = {"VBPW34S.kicad_sym", "XDCR_VBPW34S.kicad_mod", "VBPW34S.step"}
    if not expected.issubset(set(bundle.namelist())):
        raise RuntimeError("The archive is missing its symbol, footprint, or STEP model")
    for member, destination in (
        ("VBPW34S.kicad_sym", vendor / "VBPW34S.kicad_sym"),
        ("XDCR_VBPW34S.kicad_mod", pretty / "XDCR_VBPW34S.kicad_mod"),
        ("VBPW34S.step", vendor / "VBPW34S.step"),
    ):
        destination.write_bytes(bundle.read(member))

footprint = pcbnew.FootprintLoad(str(pretty), "XDCR_VBPW34S")
if footprint is None:
    raise RuntimeError("KiCad failed to load the supplied footprint")
pads = {p.GetNumber(): p for p in footprint.Pads()}
if set(pads) != {"A", "K"}:
    raise RuntimeError(f"Unexpected pad numbers: {set(pads)}")
pitch = abs(pads["A"].GetPosition().x - pads["K"].GetPosition().x) / 1e6
widths = sorted(p.GetSize().x / 1e6 for p in pads.values())
heights = sorted(p.GetSize().y / 1e6 for p in pads.values())
if abs(pitch - 7.15) > 0.01 or widths != [1.75, 1.75] or heights != [1.8, 1.8]:
    raise RuntimeError(f"Pad geometry does not match Vishay drawing: pitch={pitch}, sizes={widths}/{heights}")

candidate.mkdir(exist_ok=True)
(candidate / "fp-lib-table").write_text(
    '(fp_lib_table (lib (name "VBPW34S")(type "KiCad")'
    '(uri "${KIPRJMOD}/../vendor/VBPW34S.pretty")(options "")(descr "VBPW34S supplied library")))\n',
    encoding="utf-8",
)
(candidate / "sym-lib-table").write_text(
    '(sym_lib_table (lib (name "VBPW34S")(type "KiCad")'
    '(uri "${KIPRJMOD}/../vendor/VBPW34S.kicad_sym")(options "")(descr "VBPW34S supplied library")))\n',
    encoding="utf-8",
)
print(f"Imported VBPW34S: pad pitch {pitch:.2f} mm; pad 1.75 x 1.80 mm; candidate tables registered")
