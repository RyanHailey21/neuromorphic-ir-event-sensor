# Rev A pre-fabrication audit — 2026-09-27

**Verdict: NOT READY TO ORDER.** This review used the saved KiCad 10 files in this checkout. KiCad was closed. No schematic, PCB, or project source file was changed.

## Saved-design evidence

- PCB SHA-256: `65F58B5DC69B1B3234D7F3230113DF001C54F8C2D17A4544FACD2FB98FCFF4F7`.
- Schematic SHA-256: `741BF3440878621DAB246A26CC2F7E21FBC0FA813EE598872E87EABA5AF2AB45`.
- Direct KiCad 10.0.6 PCB DRC: 0 unconnected items; 26 warnings, all `lib_footprint_mismatch`. No copper or silkscreen errors were reported in that run. Schematic parity could not be checked.
- Direct KiCad schematic ERC: **failed to load schematic**. The companion ERC and schematic render also failed. A read-only parentheses/quotation balance check passed, but it does not establish that KiCad accepts the file.
- Fresh [top](sensor_audit_top.png) and [isometric](sensor_audit_iso.png) 3D renders of the saved PCB were reviewed. Board outline, four photodiodes, IR LED, four mounting holes, and 10-pin event header are visible.

## Release blockers

1. **IR emitter cannot be commanded.** `LED_EN` has only one PCB pad, `RG.1`. It reaches no connector, test pad, source, or other component. `RPD.2` has no net; the 100 kΩ gate pull-down is therefore open. The AO3400A gate can float, and the TSAL6200 has no defined enable control. The user specified an FPGA-controlled enable that may be pulsed. Add an accessible `LED_EN` and return connection, connect `RPD.2` to GND, update schematic and PCB, then recheck routing and DRC.
2. **Schematic cannot be loaded by KiCad CLI.** Repair it through KiCad-aware tooling, run a clean ERC, then establish zero schematic/PCB parity issues. The PCB DRC alone cannot validate electrical intent.
3. **Photodiode operating point and simulation do not match the board.** On all four channels, photodiode pad 1 (cathode in the embedded BPW34-SMD symbol) connects to the OPA381 summing input and pad 2 (anode) to VREF. The noninverting OPA381 input is also VREF, so the diode has approximately zero DC reverse bias. The SPICE deck describes the opposite diode orientation and assumes a 1.25 V reverse bias with a fixed 65 pF capacitance. Its comparator and one-shot are behavioral substitutes; only the OPA381 has a vendor macromodel. Rerun a board-faithful simulation and check the optical bandwidth/noise and actual one-shot pulse width before calling the analog function verified.
4. **Photodiode identity and footprint need reconciliation.** Per the user's Rev A decision, the intended assembly part is Vishay `VBPW34S`. The PCB and schematic values still say `VBPW34FASR`, while the footprint is `OptoDevice:Osram_BPW34S-SMD`. Confirm the Vishay pad geometry and polarity against its datasheet and update design metadata. The unfiltered VBPW34S also changes the ambient-light response assumed by the original filtered-part specification.

## Other findings

- The user confirmed the routed 2×5, 10-pin `J_FPGA` is intentional. The design specification and README still describe a 20-pin interface and signals absent from the PCB; update those documents and the FPGA harness pinout.
- Companion pinout audit found 45 references without trailing digits and one floating pad (`RPD.2`). The references can obstruct normal KiCad schematic-to-PCB update and make assembly review harder.
- The companion bounding-box placement check reported 14 overlaps and a failed score; KiCad's polygon DRC reported no courtyard violations. Resolve the score discrepancy before release, especially around the LED/Q1 and reference capacitors.
- The existing production ZIP contains copper, mask, paste, silkscreen, outline, and PTH/NPTH drill files, but it predates this audit and the required fixes. Do not upload it. Generate a fresh package after the corrected board passes ERC, schematic parity, DRC, pinout review, assembly BOM/CPL inspection, and Gerber/drill viewer review.

## Rev A decisions captured from the user

- `J_FPGA` is intentionally **10 pins**.
- Populate **Vishay VBPW34S** photodiodes.
- `LED_EN` must be a real **FPGA-controllable input**, suitable for pulsing the illuminator.

## Source data

- `neuromorphic-ir-event-sensor.kicad_pcb` and `.kicad_sch` in this checkout.
- `docs/DESIGN_SPECIFICATION.md`, `simulation/neuromorphic_afe.cir`, and the existing JLCPCB BOM/CPL.
- TI SN74LVC1G123, OPA381, TLV3202, REF3312 datasheets; Vishay VBPW34S datasheet.
