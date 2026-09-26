# Project Context & Hardware Intent

## 1. Project Goal & Intent
- **Project Name:** Neuromorphic Ir Event Sensor
- **Primary Goal:** Quad-channel neuromorphic infrared event sensor implementing asynchronous differential temporal change detection with sub-millisecond spike telemetry for low-power edge perception.
- **Target Application:** Embedded autonomous sensing, neuromorphic edge computing, and real-time event telemetry.

## 2. Electrical Specifications & Architecture
- **Power Supply Rails:** 3.3V (VCC), GND
- **Estimated Operating Voltage:** 3.3 VDC
- **Signal Architecture:**
  - Front-End: Low-noise transimpedance amplifier (TIA) with photodiode sensor array.
  - Signal Conditioning: Analog differentiators / threshold comparators for asynchronous event generation.
  - Event Output: Monostable pulse generators driving digital interfaces / FPGA headers.

## 3. Real Electronics Components & SPICE Model Verification
| Reference | Component / Value | Role | SPICE Macromodel Status |
|-----------|-------------------|------|-------------------------|
| `U` | `74LVC1G123` | Active Stage IC | Model Required / Verified in Testbench |
| `U_CMP4` | `TLV3202AIDR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_TIA4` | `OPA381AIDGKR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_CMP3` | `TLV3202AIDR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_OS_ON_TR` | `74LVC1G123` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_OS_OFF_TL` | `74LVC1G123` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_OS_OFF_BL` | `74LVC1G123` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_REF` | `REF3312AIDBZR` | Active Stage IC | Model Required / Verified in Testbench |
| `U_CMP2` | `TLV3202AIDR` | Active Stage IC | Verified (OPAx381.LIB) |
| `DPD4` | `VBPW34FASR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_TIA3` | `OPA381AIDGKR` | Active Stage IC | Verified (OPAx381.LIB) |
| `DPD3` | `VBPW34FASR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_CMP1` | `TLV3202AIDR` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_OS_OFF_BR` | `74LVC1G123` | Active Stage IC | Verified (OPAx381.LIB) |
| `U_OS_ON_BL` | `74LVC1G123` | Active Stage IC | Verified (OPAx381.LIB) |

- **Available SPICE Simulation Files:** neuromorphic_afe.cir
- **Vendor Macromodel Libraries:** OPAx381.LIB

## 4. Fabrication & Physical Constraints
- **Target Manufacturer:** JLCPCB (Standard 2-Layer / 4-Layer Process)
- **Board Outline:** 50.1 mm x 70.5 mm
- **Copper Layers:** 2
- **Component Count:** 92 footprints placed
- **Design Rule Standards:**
  - Power Netclass: Trace width $\ge 0.50\text{ mm}$, clearance $\ge 0.30\text{ mm}$
  - Analog Sensitive: Trace width $\ge 0.30\text{ mm}$, clearance $\ge 0.25\text{ mm}$
  - Digital Events: Trace width $\ge 0.25\text{ mm}$, clearance $\ge 0.20\text{ mm}$
  - Silkscreen Pad Clearance: $\ge 0.50\text{ mm}$ from all exposed copper pads

## 5. Mandatory Verification Gates
- [x] SPICE simulation with true Berkeley NGSPICE solver executed
- [x] Physical pinout and polarity audited against manufacturer datasheets
- [x] 100/100 Courtyard placement score with zero edge overhangs
- [x] KiCad DRC passed with 0 errors and 0 unconnected nets
- [x] Production Gerbers, drill files, BOM, CPL, and 3D STEP exported
