# Rev A Neuromorphic IR Event Sensor  
## Full Design Specification

**Project:** Event-driven IR tracking sensor for a 2-DOF planar robotic arm  
**Revision:** Rev A  
**Primary goal:** Demonstrate a fully hardware-generated neuromorphic optical event sensor suitable for driving a digital SNN implemented on a Tang Nano 20K FPGA  
**Sensor output:** Eight independent asynchronous 3.3 V spike channels  
**Target:** Passive 3D-printed object illuminated by the sensor board  
**Nominal target range:** 200–300 mm  
**Prototype tracking field:** approximately ±45° desired; exact Rev A optical FOV is experimentally adjustable  
**Logic supply:** 3.3 V  

---

# 1. Project objective

The purpose of Rev A is to demonstrate a genuinely event-driven optical sensor in which optical changes are converted into asynchronous hardware spikes without an MCU or FPGA generating those spikes.

The sensor performs the following conversion:

```text
Target motion / reflectance change
            ↓
940 nm reflected optical power
            ↓
4 photodiodes
            ↓
4 transimpedance amplifiers
            ↓
4 temporal adaptation / high-pass stages
            ↓
8 hardware comparators
      ON + OFF per pixel
            ↓
8 hardware monostable one-shots
            ↓
8 fixed-width digital spikes
            ↓
Tang Nano 20K FPGA
            ↓
digital SNN
            ↓
2-DOF robot control
```

The FPGA is a temporary prototyping platform for the downstream spiking neural network.

The sensor itself remains analog/event-driven.

---

# 2. System boundary

Rev A contains:

- optical illumination;
- four photosensitive channels;
- photodiode transimpedance amplification;
- temporal adaptation;
- ON-event detection;
- OFF-event detection;
- fixed-width spike generation;
- 3.3 V digital event outputs;
- analog/debug signals;
- optical/mechanical provisions for an M12 lens.

Rev A does **not** contain:

- AS5600 encoder interfaces;
- motor drivers;
- arm power electronics;
- FPGA;
- digital SNN;
- robot inverse kinematics;
- joint control.

Those belong to the downstream controller.

---

# 3. Robot configuration

The eventual robot is a **2-DOF arm operating in one vertical plane**.

Joint position feedback will be provided by:

- AS5600 absolute encoder module — Joint 1
- AS5600 absolute encoder module — Joint 2

The Tang Nano 20K will eventually receive:

```text
8 optical event inputs

AS5600 joint 1 position
AS5600 joint 2 position

↓
digital SNN / controller
↓
joint 1 command
joint 2 command
```

The AS5600 system therefore does not modify the Rev A sensor PCB.

---

# 4. Optical architecture

## 4.1 Illumination

Rev A uses active illumination from the sensor head.

Emitter:

**Vishay TSAL6200**

Nominal wavelength:

$$
\lambda \approx 940\text{ nm}
$$

The target contains no electronics or IR emitter.

Concept:

```text
Sensor head
      ↓
940 nm illumination
      ↓
passive target
      ↓
reflected IR
      ↓
receiver lens
      ↓
four photodiodes
```

---

# 5. Receiver optics

Rev A intentionally uses inexpensive, readily obtainable optics.

## 5.1 Lens

Use:

**Generic 2.8 mm focal-length M12×0.5 lens**

Requirements:

- M12×0.5 thread;
- approximately 2.8 mm EFL;
- no IR-cut filter;
- adequate transmission at 940 nm;
- adjustable focus.

The lens does not need machine-vision image quality.

Its primary purpose is to redistribute target reflection spatially across the four photodiodes.

---

# 6. Lens mounting

Use an adjustable M12 lens holder.

Required characteristics:

- M12×0.5 internal thread;
- axial focus adjustment;
- approximately 5–10 mm useful adjustment range;
- black or otherwise light-blocking material.

Do not permanently fix the lens position until the sensor has been experimentally aligned.

---

# 7. Receiver housing

The optical housing should be 3D printed.

Preferred material:

**matte black filament**

The housing should contain:

1. lens holder;
2. detector cavity;
3. hood around the receiver;
4. opaque barrier between emitter and receiver.

The housing must minimize direct coupling from the TSAL6200 into the photodiodes.

Concept:

```text
Front view

┌────────────────────────────┐
│                            │
│       M12 receiver         │
│            ○               │
│                            │
│      opaque divider        │
│            │               │
│            │               │
│            ●               │
│        TSAL6200            │
│                            │
└────────────────────────────┘
```

---

# 8. Photodiode arrangement

Use four:

**Vishay VBPW34FASR**

Arrange as:

```text
       optical image

       TL        TR

       BL        BR
```

The four detectors should be packed as closely together as practical.

Exact spacing is not considered a critical Rev A parameter because the lens focus and housing will be experimentally adjustable.

---

# 9. Channel naming

The four optical channels are:

- `TL` — top left
- `TR` — top right
- `BL` — bottom left
- `BR` — bottom right

Each optical channel generates:

- one continuous analog photodetector output;
- one ON event stream;
- one OFF event stream.

Total:

$$
4 \times 2 = 8
$$

hardware spike outputs.

---

# 10. Electrical supply

Nominal system supply:

$$
V_{\text{CC}} = 3.3\text{ V}
$$

All active electronics must operate directly from 3.3 V.

Use a continuous ground plane.

Do not intentionally split analog and digital grounds.

---

# 11. Analog reference

Use:

**Texas Instruments REF3312AIDBZR**

Reference voltage:

$$
V_{\text{REF}} = 1.25\text{ V}
$$

This replaces the earlier 1.65 V concept.

Reason:

The OPA381 input common-mode range does not guarantee correct operation with its input held at 1.65 V on a 3.3 V supply.

1.25 V provides appropriate operating margin.

Reference decoupling:

```text
REF3312 output
    |
    +--- 1 µF --- GND
    |
    +--- 100 nF - GND
```

Place both capacitors close to the reference.

---

# 12. Transimpedance amplifier

Each photodiode uses one:

**OPA381**

Quantity:

$$
4
$$

Preferred ordering package:

**OPA381AIDGKR**

or equivalent OPA381 package suitable for the intended assembly process.

---

# 13. TIA topology

Per channel:

```text
                          RF = 18.0 kΩ
                 +-------/\/\/\-------+
                 |                    |
                 |      CF = 47 pF    |
                 +---------||---------+
                 |                    |
                 |      OPA381        |
VREF = 1.25 V ---|+                OUT|---- VPHOTO_x
                 |                    |
photodiode ------|-                   |
                 +--------------------+
```

Nominal values:

$$
R_F = 18.0\,\text{k}\Omega
$$

$$
C_F = 47\text{ pF}
$$

Use:

- 18.0 kΩ, 0.1% preferred;
- 47 pF, C0G/NP0 dielectric, 5%.

The feedback capacitor must be physically adjacent to the OPA381.

---

# 14. Photodiode orientation

The photodiode should be connected so that increasing photocurrent produces an increasing `VPHOTO` level relative to `VREF`.

The photodiode should operate with reverse bias appropriate to the 1.25 V reference configuration.

Final polarity should be verified during schematic ERC and first bench test.

---

# 15. Approximate TIA relationship

Idealized behavior:

$$
V_{\text{PHOTO}} \approx V_{\text{REF}} + I_{\text{PHOTO}} R_F
$$

Therefore:

$$
V_{\text{PHOTO}} \approx 1.25 + (I_{\text{PHOTO}})(18\,000)
$$

Example:

At:

$$
I_{\text{PHOTO}} = 50\,\mu\text{A}
$$

the ideal output is:

$$
V_{\text{PHOTO}} \approx 2.15\text{ V}
$$

This leaves useful positive output headroom on a 3.3 V supply.

---

# 16. TIA decoupling

Every OPA381 gets:

- 100 nF ceramic directly between supply and ground.

Additionally provide local bulk analog decoupling:

- 10 µF near the TIA group.

Recommended analog rail:

```text
3V3
 |
ferrite bead
 |
3V3_ANALOG
```

Suggested bead:

**Murata BLM18AG601SN1D**

or equivalent 0603 ferrite bead.

---

# 17. Analog output signals

Expose:

```text
VPHOTO_TL
VPHOTO_TR
VPHOTO_BL
VPHOTO_BR
```

These are not required for basic event signaling to the FPGA but are extremely useful for:

- oscilloscope measurements;
- optical alignment;
- debugging;
- future hybrid tracking;
- characterization.

Add approximately 100 Ω series resistance before external analog debug pins if desired.

---

# 18. Temporal adaptation stage

Each `VPHOTO` signal feeds a temporal high-pass/adaptation network.

Per channel:

```text
VPHOTO_x ----- 100 nF -----+----- VEVENT_x
                           |
                          22 kΩ
                           |
                         VREF
```

Nominal values:

$$
R_A = 22\,\text{k}\Omega
$$

$$
C_A = 100\text{ nF}
$$

Therefore:

$$
\tau = R_A C_A
$$

$$
\tau = 2.2\text{ ms}
$$

and approximately:

$$
f_c = \frac{1}{2\pi R_A C_A}
$$

$$
f_c \approx 72\text{ Hz}
$$

---

# 19. Adaptation behavior

The adaptation circuit rejects static or slowly changing illumination.

At steady illumination:

$$
V_{\text{EVENT}} \rightarrow V_{\text{REF}}
$$

A sudden increase in reflected IR generates a positive transient.

A sudden decrease generates a negative transient.

Concept:

```text
Reflected light increases
        ↓
VEVENT > VREF
        ↓
ON event

Reflected light decreases
        ↓
VEVENT < VREF
        ↓
OFF event
```

---

# 20. Event thresholds

Nominal event threshold:

$$
\pm 40\text{ mV}
$$

about the 1.25 V reference.

Therefore:

$$
V_{\text{TH,ON}} = 1.29\text{ V}
$$

$$
V_{\text{TH,OFF}} = 1.21\text{ V}
$$

---

# 21. Comparator selection

Use:

**TLV3202AIDR**

This is a dual comparator.

Quantity:

$$
4
$$

Total comparator channels:

$$
4 \times 2 = 8
$$

Each photodiode channel consumes one dual comparator:

```text
Comparator A = ON event
Comparator B = OFF event
```

---

# 22. Comparator logic

ON:

```text
VEVENT_x → comparator +
1.29 V   → comparator -

output → RAW_ON_x
```

OFF:

```text
1.21 V   → comparator +
VEVENT_x → comparator -

output → RAW_OFF_x
```

Thus:

$$
V_{\text{EVENT}} > 1.29\text{ V}
$$

produces an ON assertion.

And:

$$
V_{\text{EVENT}} < 1.21\text{ V}
$$

produces an OFF assertion.

---

# 23. Threshold generation

The threshold circuits may be generated from `VREF`, `3V3_ANALOG`, and ground.

Nominal resistor networks previously selected:

Upper threshold:

```text
3.3 V
 |
499 kΩ
 |
 +------ VTH_ON
 |
10.0 kΩ
 |
1.25 V
```

Lower threshold:

```text
1.25 V
 |
10.0 kΩ
 |
 +------ VTH_OFF
 |
301 kΩ
 |
GND
```

Use 0.1% resistors for threshold-defining components.

Before PCB release, calculate the exact threshold values from the chosen E96 resistor values and record them in the schematic.

Provide test points:

```text
TP_VTH_ON
TP_VTH_OFF
```

---

# 24. Comparator hysteresis

The comparator has some inherent hysteresis, but Rev A should allow optional external hysteresis footprints.

Populate only if bench testing indicates threshold chatter.

Provide DNP footprint:

```text
RHYS_x
```

approximately:

$$
470\,\text{k}\Omega \text{ to } 2\,\text{M}\Omega
$$

depending on the desired additional hysteresis.

Default:

**DNP**

---

# 25. Raw comparator signals

Expose small test pads for:

```text
RAW_ON_TL
RAW_OFF_TL

RAW_ON_TR
RAW_OFF_TR

RAW_ON_BL
RAW_OFF_BL

RAW_ON_BR
RAW_OFF_BR
```

These test points are important because they allow the analog event detector to be observed independently of the one-shot stage.

---

# 26. One-shot stage

Raw comparator assertions are converted into fixed-width spikes.

Use:

**74LVC1G123-class retriggerable monostable**

Quantity:

$$
8
$$

One device per event signal.

Signals:

```text
RAW_ON_TL  → SPIKE_ON_TL
RAW_OFF_TL → SPIKE_OFF_TL

RAW_ON_TR  → SPIKE_ON_TR
RAW_OFF_TR → SPIKE_OFF_TR

RAW_ON_BL  → SPIKE_ON_BL
RAW_OFF_BL → SPIKE_OFF_BL

RAW_ON_BR  → SPIKE_ON_BR
RAW_OFF_BR → SPIKE_OFF_BR
```

---

# 27. One-shot timing

Nominal timing components:

$$
R_{\text{EXT}} = 8.2\,\text{k}\Omega
$$

$$
C_{\text{EXT}} = 12\text{ nF}
$$

Nominal target pulse width:

$$
t_{\text{spike}} \approx 100\,\mu\text{s}
$$

Behavioral simulations used approximately:

$$
98.4\,\mu\text{s}
$$

and produced 100 µs pulses at the simulation timestep.

---

# 28. Spike behavior

A raw comparator output may remain asserted for milliseconds.

The one-shot converts the threshold crossing into a short fixed-width event.

Example:

```text
RAW comparator

____|‾‾‾‾‾‾‾‾‾‾‾‾|____


SPIKE

____|‾|_________________
    ~100 µs
```

Thus event amplitude or target speed does not directly determine pulse width.

---

# 29. One-shot retriggering

Use retriggerable behavior.

If a new valid trigger occurs while the one-shot is active, the active period may be extended according to the selected device's behavior.

At normal Rev A event rates this is not expected to be a limiting factor.

---

# 30. FPGA event outputs

The final digital event signals are:

```text
SPIKE_ON_TL
SPIKE_OFF_TL

SPIKE_ON_TR
SPIKE_OFF_TR

SPIKE_ON_BL
SPIKE_OFF_BL

SPIKE_ON_BR
SPIKE_OFF_BR
```

Voltage:

```text
LOW ≈ 0 V
HIGH ≈ 3.3 V
```

Nominal pulse width:

```text
~100 µs
```

---

# 31. Spike output series resistors

Place one resistor between each one-shot output and the board connector.

Nominal:

$$
R_{\text{OUT}} = 150\,\Omega
$$

Acceptable prototype range:

$$
100\,\Omega \text{ to } 220\,\Omega
$$

Quantity:

$$
8
$$

Purpose:

- reduce ringing;
- limit transient current;
- improve cable behavior;
- protect against accidental contention.

Use 150 Ω as the default population value.

---

# 32. FPGA connector

Use a keyed:

**2×5, 2.54 mm header**

Pin assignment:

| Pin | Signal |
|---:|---|
| 1 | GND |
| 2 | 3V3 |
| 3 | SPIKE_ON_TL |
| 4 | SPIKE_OFF_TL |
| 5 | SPIKE_ON_TR |
| 6 | SPIKE_OFF_TR |
| 7 | SPIKE_ON_BL |
| 8 | SPIKE_OFF_BL |
| 9 | SPIKE_ON_BR |
| 10 | SPIKE_OFF_BR |

Use a physical key or shrouded header if practical.

---

# 33. Tang Nano 20K FPGA interface

Each event input must enter a 3.3 V-compatible GPIO.

Inside the FPGA, each asynchronous event line should first pass through a synchronizer:

```text
sensor spike
     ↓
FF1
     ↓
FF2
     ↓
edge detector
     ↓
single-clock event
     ↓
digital SNN input neuron
```

Conceptual RTL:

```verilog
sync1   <= sensor_spike;
sync2   <= sync1;
sync2_d <= sync2;

event_pulse <= sync2 & ~sync2_d;
```

The physical sensor pulse is about 100 µs, so FPGA capture margin is extremely large at normal FPGA clock frequencies.

---

# 34. SNN input mapping

Use eight independent SNN input channels:

```text
Neuron input 0 = TL_ON
Neuron input 1 = TL_OFF

Neuron input 2 = TR_ON
Neuron input 3 = TR_OFF

Neuron input 4 = BL_ON
Neuron input 5 = BL_OFF

Neuron input 6 = BR_ON
Neuron input 7 = BR_OFF
```

Do not combine them in hardware on the sensor board.

Preserving all eight signals gives maximum flexibility for SNN experimentation.

---

# 35. Analog debug connector

Use a separate 1×6 header.

Pin assignment:

| Pin | Signal |
|---:|---|
| 1 | GND |
| 2 | VREF |
| 3 | VPHOTO_TL |
| 4 | VPHOTO_TR |
| 5 | VPHOTO_BL |
| 6 | VPHOTO_BR |

This header is intended primarily for oscilloscopes and characterization.

---

# 36. Event-node test pads

Also provide PCB test pads for:

```text
VEVENT_TL
VEVENT_TR
VEVENT_BL
VEVENT_BR
```

These are particularly important when tuning:

- adaptation time constant;
- threshold;
- optical focus;
- LED intensity.

---

# 37. IR LED

Emitter:

**TSAL6200**

Wavelength:

$$
940\text{ nm}
$$

The LED should be physically adjacent to the receiver but optically isolated from it.

---

# 38. LED driver

Use:

**AO3400A**

as a low-side N-channel MOSFET.

Topology:

```text
3V3
 |
RLED
 |
TSAL6200
 |
AO3400A
 |
GND
```

MOSFET gate:

```text
LED_EN ---- 100 Ω ---- gate

gate ---- 100 kΩ ---- GND
```

---

# 39. LED resistor

Initial value:

$$
R_{\text{LED}} = 82\,\Omega
$$

Use a 1206 footprint.

The LED resistor is deliberately considered a tuning component.

Provide space permitting for an alternate resistor footprint or make the resistor easy to replace manually.

Suggested experimental alternatives:

```text
68 Ω
82 Ω
100 Ω
150 Ω
```

---

# 40. LED control

Provide `LED_EN`.

For initial static testing, `LED_EN` can be held high.

Future versions may modulate the LED to improve ambient-light rejection.

Modulating illumination does not violate the hardware-spiking nature of the sensor.

The analog circuitry still generates all event spikes independently.

---

# 41. Power architecture

Recommended:

```text
                   +------ IR LED
                   |
3V3_IN ------------+
                   |
                   +-- ferrite bead --> 3V3_ANALOG
                                          |
                         +----------------+----------------+
                         |                |                |
                      OPA381          TLV3202          REF3312
```

One-shot logic may run directly from 3V3 or from the filtered rail depending on layout.

Preferred:

- analog front end on `3V3_ANALOG`;
- one-shots on regular `3V3`;
- common ground plane.

---

# 42. Supply decoupling

Every IC receives:

$$
100\text{ nF}
$$

directly across supply and ground.

Additionally:

Analog group:

$$
10\,\mu\text{F}
$$

Logic/one-shot group:

$$
10\,\mu\text{F}
$$

Reference:

```text
1 µF
100 nF
```

LED supply should also have local bulk capacitance:

```text
4.7–10 µF
```

near the emitter/driver if space permits.

---

# 43. Grounding

Use:

**one continuous ground plane**

Do not create physically isolated AGND and DGND planes.

Instead, control noise through:

- placement;
- short return paths;
- decoupling;
- power filtering;
- separation of high-current LED routing from photodiode input nodes.

---

# 44. Critical PCB layout rule

The most sensitive electrical node is:

```text
photodiode → OPA381 inverting input
```

This trace must be extremely short.

Prefer:

```text
photodiode
   ↓
2–8 mm trace
   ↓
OPA381
```

where mechanically possible.

Do not route digital signals near this node.

---

# 45. Feedback placement

`RF` and `CF` must be located directly adjacent to the OPA381.

Minimize loop area:

```text
OPA381 OUT
  ↓
RF || CF
  ↓
OPA381 IN-
```

No long traces.

---

# 46. Board partitioning

Recommended physical organization:

```text
OPTICAL END

┌──────────────────────────────────────────┐
│             receiver region              │
│                                          │
│       PD_TL             PD_TR            │
│                                          │
│       PD_BL             PD_BR            │
│                                          │
│                IR LED                    │
├──────────────────────────────────────────┤
│ TIA_TL   TIA_TR   TIA_BL   TIA_BR        │
│                                          │
│       temporal adaptation circuits       │
│                                          │
│          TLV3202 comparators             │
│                                          │
│              one-shots                   │
│                                          │
│ FPGA header          debug header        │
└──────────────────────────────────────────┘
```

---

# 47. Digital/analog separation

Keep:

```text
one-shot outputs
FPGA connector traces
LED switching traces
```

away from:

```text
photodiode inputs
TIA inverting nodes
threshold references
```

Do not route a 3.3 V spike trace beneath the photodiode input circuitry if avoidable.

---

# 48. Photodiode copper

Avoid excessive copper connected to the inverting photodiode node.

Additional capacitance on this node can degrade TIA stability and noise performance.

Do not pour ground unnecessarily close to the sensitive input trace unless deliberately implementing a guard structure.

---

# 49. Test points

Rev A must include probe pads for at least:

```text
3V3
3V3_ANALOG
GND
VREF

VTH_ON
VTH_OFF

VPHOTO_TL
VPHOTO_TR
VPHOTO_BL
VPHOTO_BR

VEVENT_TL
VEVENT_TR
VEVENT_BL
VEVENT_BR

RAW_ON_TL
RAW_OFF_TL
RAW_ON_TR
RAW_OFF_TR
RAW_ON_BL
RAW_OFF_BL
RAW_ON_BR
RAW_OFF_BR

SPIKE_ON_TL
SPIKE_OFF_TL
SPIKE_ON_TR
SPIKE_OFF_TR
SPIKE_ON_BL
SPIKE_OFF_BL
SPIKE_ON_BR
SPIKE_OFF_BR
```

Use small loop or pad test points rather than large through-hole posts where board size matters.

---

# 50. Prototype tuning footprints

Rev A should allow adaptation values to be changed easily.

Nominal:

```text
22 kΩ
100 nF
```

Suggested alternatives:

```text
R:
10 kΩ
22 kΩ
47 kΩ

C:
47 nF
100 nF
220 nF
```

Optional parallel footprints or easily replaceable 0603 components are recommended.

---

# 51. Threshold tuning

Nominal event threshold:

$$
40\text{ mV}
$$

The board should make the threshold divider resistors accessible enough to change during characterization.

Potential experimental threshold range:

$$
20\text{ mV to } 100\text{ mV}
$$

No potentiometer is required for Rev A unless convenient.

Fixed precision resistors are preferred for low noise and repeatability.

---

# 52. One-shot tuning

Nominal:

```text
8.2 kΩ
12 nF
```

Target:

```text
~100 µs
```

Possible experimental spike widths:

```text
50 µs
100 µs
200 µs
```

The PCB should allow timing components to be changed easily.

100 µs remains the default Rev A value.

---

# 53. Primary BOM

| Qty | Reference | Component | Value / Part |
|---:|---|---|---|
| 4 | DPD1–DPD4 | IR photodiode | VBPW34FASR |
| 4 | U_TIA1–U_TIA4 | TIA amplifier | OPA381AIDGKR |
| 4 | U_CMP1–U_CMP4 | Dual comparator | TLV3202AIDR |
| 8 | U_OS1–U_OS8 | Retriggerable one-shot | 74LVC1G123-class |
| 1 | U_REF | Reference | REF3312AIDBZR |
| 1 | LED1 | IR emitter | TSAL6200 |
| 1 | Q1 | N-MOSFET | AO3400A |
| 1 | FB1 | Ferrite bead | BLM18AG601SN1D |
| 4 | RF1–RF4 | TIA feedback resistor | 18.0 kΩ, 0.1% |
| 4 | CF1–CF4 | TIA feedback capacitor | 47 pF, C0G |
| 4 | RA1–RA4 | Adaptation resistor | 22 kΩ |
| 4 | CA1–CA4 | Adaptation capacitor | 100 nF |
| 8 | ROS1–ROS8 | One-shot timing resistor | 8.2 kΩ |
| 8 | COS1–COS8 | One-shot timing capacitor | 12 nF |
| 8 | ROUT1–ROUT8 | Spike series resistor | 150 Ω |
| 1 | RLED | LED resistor | 82 Ω, 1206 |
| 1 | RG | MOSFET gate resistor | 100 Ω |
| 1 | RPD | MOSFET gate pulldown | 100 kΩ |
| 1 | RTHP_A | ON threshold | 499 kΩ, 0.1% |
| 1 | RTHP_B | ON threshold | 10.0 kΩ, 0.1% |
| 1 | RTHN_A | OFF threshold | 301 kΩ, 0.1% |
| 1 | RTHN_B | OFF threshold | 10.0 kΩ, 0.1% |
| 1 | CREF1 | Reference decoupling | 1 µF |
| 1 | CREF2 | Reference decoupling | 100 nF |
| 1/IC | CDEC | IC decoupling | 100 nF |
| 2+ | CBULK | Bulk supply | 10 µF |
| 1 | J_FPGA | FPGA connector | keyed 2×5, 2.54 mm |
| 1 | J_DEBUG | analog debug | 1×6, 2.54 mm |
| 1 | — | Receiver lens | 2.8 mm M12, no IR-cut |
| 1 | — | Lens mount | M12×0.5 adjustable holder |

---

# 54. Optional / DNP BOM

Provide footprints where useful for:

- comparator hysteresis resistors;
- alternate LED resistor;
- alternate adaptation R/C;
- alternate one-shot R/C;
- additional analog-output series resistors;
- 940 nm bandpass filter mounting provision if mechanical design permits.

These are DNP by default.

---

# 55. FPGA-side input treatment

The Tang Nano must not use the raw asynchronous lines directly in deep synchronous logic.

Every event channel gets:

```text
asynchronous pin
      ↓
2-stage synchronizer
      ↓
edge detector
      ↓
one FPGA-clock pulse
```

The sensor board already generates approximately 100 µs pulses, so pulse stretching in the FPGA is unnecessary.

---

# 56. FPGA SNN architecture

Initial conceptual mapping:

```text
TL_ON  ─┐
TL_OFF ─┤
TR_ON  ─┤
TR_OFF ─┤
BL_ON  ─┤→ digital SNN → joint-output neurons
BL_OFF ─┤
BR_ON  ─┤
BR_OFF ─┘
```

Potential downstream output populations:

```text
J1_POS
J1_NEG
J2_POS
J2_NEG
```

The exact SNN is intentionally outside this sensor-board specification.

---

# 57. Encoder interface

The two AS5600 modules will connect to the FPGA/controller, not the sensor board.

Because two standard AS5600 devices generally share the same I²C address, the controller should eventually use either:

- two independent I²C interfaces;
- an I²C mux;
- another available AS5600 output mode if appropriate.

For the Tang Nano prototype, two FPGA I²C masters are acceptable.

---

# 58. Motor-control relationship

The eventual architecture is:

```text
8 event inputs
        ↓
digital SNN
        ↓
desired joint activity
        ↓
motor-control layer
        ↑
AS5600 joint states
        ↓
2-DOF arm
```

The exact motor drivers and control law will be specified separately.

---

# 59. Rev A optical target

The target may initially be a simple 3D-printed object.

For easiest demonstration:

- use a relatively light-colored surface;
- avoid very glossy geometry initially;
- approximately 30–50 mm target dimensions are reasonable for early tests.

Target dimensions are not frozen because Rev A is intended to demonstrate event behavior, not optimize absolute tracking performance.

---

# 60. Nominal operating distance

Prototype optical testing:

$$
200\text{ to } 300\text{ mm}
$$

Nominal characterization distance:

$$
250\text{ mm}
$$

---

# 61. Tracking FOV

Desired approximate acquisition field:

$$
\pm 45^\circ
$$

Rev A does not guarantee exact ±45° optical linearity.

The inexpensive M12 lens is deliberately treated as a prototype optical component.

Functional requirement:

The sensor should demonstrate distinguishable quadrant responses over a sufficiently wide angular range to drive a 2-DOF tracking experiment.

---

# 62. Event-sensor success criterion

The primary Rev A success criterion is **not precision tracking accuracy**.

Rev A succeeds if:

1. static illumination produces few or no persistent events;
2. increasing reflected IR produces hardware ON spikes;
3. decreasing reflected IR produces hardware OFF spikes;
4. target motion produces spatially meaningful differences between the four channels;
5. all spikes are generated without MCU/FPGA intervention;
6. the Tang Nano reliably receives all eight event streams;
7. spike activity can drive an experimental digital SNN.

---

# 63. Electrical verification plan

## Stage 1 — Power

Before installing optics:

Verify:

```text
3V3
3V3_ANALOG
VREF ≈ 1.25 V
VTH_ON ≈ 1.29 V
VTH_OFF ≈ 1.21 V
```

Check supply current.

Check for oscillation.

---

# 64. TIA verification

Illuminate each detector individually.

Observe:

```text
VPHOTO_x
```

Requirements:

- stable output;
- output increases or decreases consistently with light according to intended polarity;
- no rail saturation under ordinary indoor illumination;
- no sustained oscillation.

---

# 65. Adaptation verification

Apply a step change in IR illumination.

Observe:

```text
VPHOTO_x
VEVENT_x
```

Expected:

`VPHOTO_x` changes and remains at the new level.

`VEVENT_x` produces a transient and returns toward:

$$
1.25\text{ V}
$$

with approximately:

$$
2.2\text{ ms}
$$

time constant.

---

# 66. Comparator verification

Apply sufficient positive and negative optical transitions.

Verify:

```text
RAW_ON_x
RAW_OFF_x
```

Positive transient:

```text
RAW_ON asserted
```

Negative transient:

```text
RAW_OFF asserted
```

Check for chatter.

If excessive chatter occurs, populate optional hysteresis.

---

# 67. One-shot verification

Measure:

```text
SPIKE_ON_x
SPIKE_OFF_x
```

Expected pulse width:

approximately:

$$
100\,\mu\text{s}
$$

Pulse amplitude:

approximately 3.3 V logic.

Pulse width should remain substantially constant even when the raw comparator duration changes.

---

# 68. FPGA verification

Connect one event output at a time.

Verify:

- no pin overvoltage;
- synchronizer captures every pulse;
- exactly one FPGA event occurs per sensor spike;
- no duplicate edge detection.

Then connect all eight channels.

---

# 69. Optical verification

Install the lens and target.

At approximately 250 mm:

Move target:

```text
left
right
up
down
toward center
away from center
```

Verify that different quadrant channels produce distinguishable event patterns.

Exact tracking calibration is secondary to proving spatial event encoding.

---

# 70. Recommended oscilloscope measurements

During bring-up capture:

### Channel waveform

```text
VPHOTO
VEVENT
RAW_ON
SPIKE_ON
```

and separately:

```text
VPHOTO
VEVENT
RAW_OFF
SPIKE_OFF
```

These captures will directly demonstrate the event-sensor concept.

---

# 71. Expected demonstration

A convincing final demonstration should show:

```text
Target moves left
     ↓
specific quadrant optical response changes
     ↓
hardware ON/OFF spikes appear
     ↓
Tang Nano receives events
     ↓
digital SNN produces joint command
     ↓
robot follows target
```

No processor is required to convert optical intensity changes into spikes.

---

# 72. Design variables intentionally left tunable

The architecture is frozen.

The following values are prototype tuning variables:

### Optical
- lens focus;
- target dimensions;
- lens-to-photodiode spacing;
- LED/receiver mechanical spacing;
- hood geometry.

### Electrical
- LED resistor;
- adaptation R/C;
- event threshold;
- one-shot width.

These are not unresolved architecture choices.

They are normal calibration variables.

---

# 73. Frozen Rev A architecture summary

```text
3.3 V POWER
   │
   ├── REF3312 → 1.25 V analog reference
   │
   ├── TSAL6200 + AO3400A → 940 nm illumination
   │
   └── SENSOR ARRAY
          │
          ├── VBPW34FASR TL → OPA381 → VPHOTO_TL
          │                       ↓
          │                   adaptation
          │                       ↓
          │                 ON/OFF comparator
          │                       ↓
          │                   two one-shots
          │                       ↓
          │                TL_ON / TL_OFF
          │
          ├── VBPW34FASR TR → same chain
          │
          ├── VBPW34FASR BL → same chain
          │
          └── VBPW34FASR BR → same chain

8 EVENT OUTPUTS
      ↓
Tang Nano 20K
      ↓
Digital SNN
      ↑
2 × AS5600 joint feedback
      ↓
2-DOF arm controller
```

---

# 74. Design status

**Rev A architecture: FROZEN**

Ready for:

1. KiCad schematic capture
2. ERC
3. footprint assignment
4. PCB mechanical definition
5. placement
6. routing
7. BOM export
8. fabrication review
9. prototype assembly
10. bench characterization

The architecture should not be reopened unless schematic review, simulation, component availability, or bench testing identifies a concrete technical problem.
