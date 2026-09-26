# Neuromorphic Infrared Event Sensor (Rev A)

An analog front-end (AFE) neuromorphic infrared event sensor board designed in KiCad 10. The board implements biologically-inspired temporal contrast sensing across four quadrants (Top-Left, Top-Right, Bottom-Left, Bottom-Right), transducing rapid dynamic changes in infrared illumination into asynchronous digital spike trains suitable for direct FPGA processing.

> **Full Engineering Design Specification**: See [`docs/DESIGN_SPECIFICATION.md`](docs/DESIGN_SPECIFICATION.md) for the frozen 74-section system boundary, optical architecture, TIA/adaptation/comparator parameters, FPGA synchronizer RTL, and verification plans.

| 3D Isometric View | 3D Top View |
| :---: | :---: |
| ![3D Isometric](docs/images/sensor_3d_iso.png?raw=true&v=4) | ![3D Top](docs/images/sensor_3d_top.png?raw=true&v=4) |

---

## 1. System Overview & Theory of Operation

### Architecture Pipeline
Each quadrant operates through an independent analog signal chain:
```
[Photodiode Pair]
        │
        ▼
[Transimpedance Amplifier (TIA)]  ──> OPA356 / ADA4899 High-Bandwidth Stage
        │
        ▼
[High-Pass Differentiator (AC Coupling)] ──> Extracts Temporal Contrast d(ln I)/dt
        │
        ├──> (+) Positive Threshold Comparator (TLV3501/MAX9012) ──> ON Spike
        └──> (-) Negative Threshold Comparator (TLV3501/MAX9012) ──> OFF Spike
        │
        ▼
[Monostable Pulse Shaper (74LVC1G123)] ──> Generates Calibrated Digital Pulses (~100 ns)
        │
        ▼
[Digital SPIKE Interface] ──> 2x10 Pin Header (J_FPGA)
```

### Optical Quadrants
- **TL (Top-Left)**: Quadrant 1
- **TR (Top-Right)**: Quadrant 2
- **BL (Bottom-Left)**: Quadrant 3
- **BR (Bottom-Right)**: Quadrant 4
- **Center Optical Barrier**: Keep-out line ($Y = 27.2\text{ mm}$) separating optical photodiodes from digital pulse-shaping logic with $>1.2\text{ mm}$ clearance.

---

## 2. Hardware Specifications

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Dimensions** | 50.0 mm × 70.0 mm | Rectangular form factor, 4 × M3 mounting holes at corners (3.5 mm inset) |
| **Layer Count** | 2 Layers | Top (`F.Cu`), Bottom (`B.Cu`) |
| **Copper Weight** | 1 oz (35 µm) | Standard FR4 substrate, 1.6 mm thickness |
| **Ground Pours** | Dual solid flooded planes | Top and bottom ground planes interconnected with low-impedance stitching |
| **Minimum Trace / Space** | 0.20 mm / 0.20 mm | 100% compliant with standard JLCPCB / PCBWay manufacturing rules |
| **Minimum Drill / Annular** | 0.30 mm drill / 0.60 mm pad | Standard via size throughout |
| **Silkscreen Finish** | Cleaned Front Silkscreen | Small 0402/0603 passive and dense IC reference designators hidden on `F.SilkS` (preserved on `F.Fab` for assembly), zero silkscreen-to-pad clipping |
| **Supply Voltage** | +3.3 V DC | Sourced via pin 2 of `J_FPGA` |
| **Power Consumption** | < 120 mA (quiescent) | Ferrite-bead isolated analog rail (`FB1`) |

---

## 3. Connector Pinouts

### J_FPGA: Digital Event Output Header (2x10, 2.54 mm Pitch)
Direct connection to FPGA GPIO bank.

| Pin | Net Name | Type | Description |
| :---: | :--- | :---: | :--- |
| **1** | `GND` | Power | System Ground |
| **2** | `3V3` | Power | +3.3 V Main Power Input |
| **3** | `SPIKE_ON_TL` | Output | Quadrant TL Positive Contrast Event |
| **4** | `SPIKE_OFF_TL` | Output | Quadrant TL Negative Contrast Event |
| **5** | `SPIKE_ON_TR` | Output | Quadrant TR Positive Contrast Event |
| **6** | `SPIKE_OFF_TR` | Output | Quadrant TR Negative Contrast Event |
| **7** | `SPIKE_ON_BL` | Output | Quadrant BL Positive Contrast Event |
| **8** | `SPIKE_OFF_BL` | Output | Quadrant BL Negative Contrast Event |
| **9** | `SPIKE_ON_BR` | Output | Quadrant BR Positive Contrast Event |
| **10** | `SPIKE_OFF_BR` | Output | Quadrant BR Negative Contrast Event |
| **11** | `GND` | Power | Digital Return Ground |
| **12** | `AER_REQ` | Output | Asynchronous Address-Event Request Line |
| **13** | `AER_ACK` | Input | Asynchronous Address-Event Acknowledge |
| **14** | `RST_N` | Input | Active-Low Hardware Reset |
| **15** | `ADDR_0` | Output | Quadrant Address Bit 0 |
| **16** | `ADDR_1` | Output | Quadrant Address Bit 1 |
| **17** | `POLARITY` | Output | Spike Polarity Indicator (1 = ON, 0 = OFF) |
| **18** | `CLK_SYNC` | Input | Optional FPGA Synchronous Sampling Clock |
| **19** | `GND` | Power | System Ground |
| **20** | `3V3_AUX` | Power | Optional Auxiliary 3.3V Monitoring Rail |

### J_DEBUG: Analog Front-End Probe Header (1x6, 2.54 mm Pitch)
Convenient oscilloscope probe points for calibration and signal integrity checking.

| Pin | Net Name | Type | Description |
| :---: | :--- | :---: | :--- |
| **1** | `GND` | Ground | Probe Ground Reference |
| **2** | `VREF` | Analog | Mid-Rail Analog Bias Reference (~1.65 V) |
| **3** | `VPHOTO_TL` | Analog | Transimpedance Output: TL Quadrant |
| **4** | `VPHOTO_TR` | Analog | Transimpedance Output: TR Quadrant |
| **5** | `VPHOTO_BL` | Analog | Transimpedance Output: BL Quadrant |
| **6** | `VPHOTO_BR` | Analog | Transimpedance Output: BR Quadrant |

---

## 4. Verification Status & DRC Sign-Off

The board has been thoroughly verified using KiCad 10 CLI verification:
- **Electrical Connections**: 62 nets, 268 pins mapped, 874 track segments, 83 vias.
- **Unconnected Nets**: **0** (100% routed).
- **Short Circuits**: **0**.
- **Clearance Violations**: **0**.
- **Silkscreen Violations**: **0** (0 pad overlaps, 0 clipping warnings).
- **Physical Placement**: 100/100 PASS (0 courtyard collisions, connectors inset $\ge 2.0\text{ mm}$ from board edge, mounting hole clearances $\ge 2.5\text{ mm}$).

---

## 5. Turnkey Production Package

Ready-to-manufacture files are located in the `production/` and `gerbers/` directories:
- **Gerbers & Drill Archive**: `production/neuromorphic-ir-event-sensor-revA-gerber.zip`
- **Bill of Materials**: `production/neuromorphic-ir-event-sensor-bom.csv` (92 components, 27 unique groups)
- **Pick-and-Place (CPL)**: `production/neuromorphic-ir-event-sensor-cpl.csv`

---

## 6. How to Build & Verify (CLI Commands)

### Run PCB Design Rule Check (DRC)
```powershell
kicad-cli pcb drc --format json -o reports/drc_report.json neuromorphic-ir-event-sensor.kicad_pcb
```

### Export Gerbers and Drill Files
```powershell
kicad-cli pcb export gerbers -o gerbers/ neuromorphic-ir-event-sensor.kicad_pcb
kicad-cli pcb export drill -o gerbers/ neuromorphic-ir-event-sensor.kicad_pcb
```

### Render Photorealistic 3D Views
```powershell
kicad-cli pcb render --side top --width 1920 --height 1080 -o render_top.png neuromorphic-ir-event-sensor.kicad_pcb
kicad-cli pcb render --rotate -45,0,45 --width 1920 --height 1080 -o render_iso.png neuromorphic-ir-event-sensor.kicad_pcb
```
