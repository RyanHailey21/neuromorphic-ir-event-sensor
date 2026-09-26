# Neuromorphic Infrared Event Sensor (Rev A)

An analog front-end (AFE) neuromorphic infrared event sensor board designed in KiCad 10. The board implements biologically-inspired temporal contrast sensing across four quadrants (Top-Left, Top-Right, Bottom-Left, Bottom-Right), transducing rapid dynamic changes in infrared illumination into asynchronous digital spike trains suitable for direct FPGA processing.

> **Full Engineering Design Specification**: See [`docs/DESIGN_SPECIFICATION.md`](docs/DESIGN_SPECIFICATION.md) for the frozen 74-section system boundary, optical architecture, TIA/adaptation/comparator parameters, FPGA synchronizer RTL, and verification plans.

| 3D Isometric View | 3D Top View |
| :---: | :---: |
| ![3D Isometric](docs/images/sensor_3d_iso.png?raw=true&v=5) | ![3D Top](docs/images/sensor_3d_top.png?raw=true&v=5) |

---

## 1. System Overview & Theory of Operation

### Architecture Pipeline
Each quadrant operates through an independent analog signal chain:
```
[Photodiode Pair (BPW34S)]
        │
        ▼
[Transimpedance Amplifier (TIA)]  ──> OPA381 Precision Stage (RF = 18.0k, CF = 47pF, VREF = 1.25V)
        │
        ▼
[High-Pass Differentiator (AC Coupling)] ──> Extracts Temporal Contrast (RA = 22.0k, CA = 100nF, tau = 2.2ms)
        │
        ├──> (+) Positive Threshold Comparator (TLV3202, VTH_ON = 1.29V) ──> ON Event
        └──> (-) Negative Threshold Comparator (TLV3202, VTH_OFF = 1.21V) ──> OFF Event
        │
        ▼
[Monostable Pulse Shaper (74LVC1G123)] ──> Generates Calibrated Digital Spikes (~100 µs)
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
| **2** | `VREF` | Analog | Precision Low-Noise Bias Reference (1.250 V, REF3312) |
| **3** | `VPHOTO_TL` | Analog | Transimpedance Output: TL Quadrant |
| **4** | `VPHOTO_TR` | Analog | Transimpedance Output: TR Quadrant |
| **5** | `VPHOTO_BL` | Analog | Transimpedance Output: BL Quadrant |
| **6** | `VPHOTO_BR` | Analog | Transimpedance Output: BR Quadrant |

---

## 4. Circuit Simulation & SPICE Verification

The analog front-end (AFE) and asynchronous spike generation stages have undergone complete SPICE and physical state-space simulation.

> **Detailed Engineering Report**: See [`docs/SIMULATION_REPORT.md`](docs/SIMULATION_REPORT.md) for complete analytical derivations, phase margin calculations, and drift immunity proofs.

### Simulation Verification Highlights (Berkeley NGSPICE 46 & Analytical MNA):
- **TIA Stability & Phase Margin**: **89.1° phase margin** at 7.17 MHz crossover frequency ($C_F = 47\text{ pF} \gg C_{F,opt} = 5.86\text{ pF}$). The transimpedance amplifier is strongly overdamped, ensuring zero ringing and unconditional stability.
- **Closed-Loop Bandwidth**: **190.55 kHz** (-3dB cutoff in NGSPICE AC analysis), passing sub-microsecond optical contrast edges while filtering RF noise.
- **Temporal Adaptation**: High-pass cutoff at **69.18 Hz** ($\tau_A = 2.20\text{ ms}$), rejecting steady-state ambient illumination and environmental light drift up to $1.01\,\mu\text{A}/\text{ms}$ with **zero false spikes**.
- **Asynchronous Digital Spikes**: The 74LVC1G123 monostable generates calibrated **$145\,\mu\text{s}$ digital CMOS pulses ($0\text{ V} \rightarrow 3.3\text{ V}$)** with $< 25\text{ ns}$ comparator propagation delay.

| Full AFE Transient Response (NGSPICE 46) | AC Stability & Bode Response (NGSPICE 46) |
| :---: | :---: |
| ![Transient Simulation](docs/images/neuromorphic_afe_transient_response.png?raw=true&v=2) | ![Bode Stability](docs/images/neuromorphic_afe_frequency_response.png?raw=true&v=2) |

| Microsecond-Scale Spike Timing Detail (NGSPICE 46) |
| :---: |
| ![Spike Detail](docs/images/neuromorphic_afe_spike_detail.png?raw=true&v=2) |

### Companion Simulation Files:
- **SPICE Netlist**: [`simulation/neuromorphic_afe.cir`](simulation/neuromorphic_afe.cir) (native netlist executed via Berkeley NGSPICE 46 / PySpice)
- **NGSPICE Runner**: [`simulation/run_spice_simulation.py`](simulation/run_spice_simulation.py) (`python simulation/run_spice_simulation.py`)
- **Companion Analytical Simulator**: [`simulation/simulate_afe.py`](simulation/simulate_afe.py) (`python simulation/simulate_afe.py`)

---

## 5. Verification Status & DRC Sign-Off

The board has been thoroughly verified using KiCad 10 CLI verification:
- **Electrical Connections**: 62 nets, 268 pins mapped, 874 track segments, 83 vias.
- **Unconnected Nets**: **0** (100% routed).
- **Short Circuits**: **0**.
- **Clearance Violations**: **0**.
- **Silkscreen Violations**: **0** (0 pad overlaps, 0 clipping warnings).
- **Physical Placement**: 100/100 PASS (0 courtyard collisions, connectors inset $\ge 2.0\text{ mm}$ from board edge, mounting hole clearances $\ge 2.5\text{ mm}$).

---

## 6. Turnkey Production Package

Ready-to-manufacture files are located in the `production/` and `gerbers/` directories:
- **3D CAD STEP Model (Full Assembly)**: [`production/neuromorphic-ir-event-sensor-revA.step`](production/neuromorphic-ir-event-sensor-revA.step) *(Ready for direct import into Onshape, SolidWorks, or FreeCAD for mechanical enclosure/lens housing modeling)*
- **Gerbers & Drill Archive**: `production/neuromorphic-ir-event-sensor-revA-gerber.zip`
- **Bill of Materials**: `production/neuromorphic-ir-event-sensor-bom.csv` (92 components, 27 unique groups)
- **Pick-and-Place (CPL)**: `production/neuromorphic-ir-event-sensor-cpl.csv`

---

## 7. How to Build & Verify (CLI Commands)

### Run PCB Design Rule Check (DRC)
```powershell
kicad-cli pcb drc --format json -o reports/drc_report.json neuromorphic-ir-event-sensor.kicad_pcb
```

### Export Gerbers and Drill Files
```powershell
kicad-cli pcb export gerbers -o gerbers/ neuromorphic-ir-event-sensor.kicad_pcb
kicad-cli pcb export drill -o gerbers/ neuromorphic-ir-event-sensor.kicad_pcb
```

### Run Berkeley NGSPICE 46 Circuit Simulation
```powershell
python simulation/run_spice_simulation.py
```

### Run Python Discrete State-Space Simulator
```powershell
python simulation/simulate_afe.py
```
