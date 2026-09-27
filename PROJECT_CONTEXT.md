# Neuromorphic IR Event Sensor — project intent

## Rev A function

Four Vishay VBPW34S photodiodes feed four OPA381 transimpedance amplifiers. Each channel compares temporal change against ON and OFF thresholds and produces two short FPGA event pulses through SN74LVC1G123 one-shots. A 10-pin J1 carries power and eight event outputs. A separate J3 accepts a 3.3 V FPGA `LED_EN` pulse train to switch the TSAL6200 IR emitter through AO3400A. J2 exposes analog debug signals.

The architecture and component values come from `docs/DESIGN_SPECIFICATION.md` and the user's explicit Rev A decisions. The older root PCB and schematic are historical artifacts, not design authority. The active candidate is `headless_candidate/`.

## Mechanical and fabrication intent

- Two copper layers; 50 × 70 mm board with 3 mm rounded corners.
- Four M3 board mounts; two M2 lens holder mounts on 20 mm spacing, confirmed by the user.
- JLCPCB is the tentative fabricator. Order service, assembly scope, stackup, finish, quantity, and component sourcing remain to be established against its current contract.
- VBPW34S footprint came from the user supplied `VBPW34S.zip`. Its 8.9 mm solder pad span matches the Vishay drawing. Pad labels and polarity marker were corrected to Vishay's top view: anode at local left, cathode at local right.
- Eight optional 2 MΩ hysteresis resistors are DNP.

## Current candidate checks (2026-09-27)

- ERC: 0 errors, 0 warnings. ERC excludes the SPICE model and footprint filter checks.
- PCB DRC after fresh programmatic routing and final ground fills: 0 violations, 0 unconnected, 0 schematic parity issues.
- Companion pinout and polarity audit: passed. The VBPW34S pad identity was also checked against the manufacturer drawing because the supplied footprint had reversed labels.
- The photodiode body STEP model is available under `vendor/`, but the board currently has no linked model for D1–D4, so 3D renders cannot prove their assembly orientation.

## Release gates still open

- Manufacturer model based circuit simulation required by KiCad Companion Rule 12 is incomplete. OPA381 and REF3312 models were found. TI's TLV3202-Q1 PSpice archive was downloaded, but it has not been converted into a verified usable dual-comparator netlist. VBPW34S, TSAL6200, and AO3400A lack confirmed manufacturer SPICE models. The SN74LVC1G123 official HSPICE model also needs compatibility work for the intended simulator.
- Assembly BOM sourcing is incomplete. Most passives and connectors have no chosen manufacturer part number, and no populated part has an LCSC number in the candidate spec. The JLCPCB placement preview must verify polarity and rotation of every assembled part, especially VBPW34S.
- No manufacturing package has been released. See `reports/REV_A_CANDIDATE_STATUS_2026-09-27.md` for the current evidence and remaining work.
