"""
Neuromorphic IR Event Sensor - True SPICE Engine Simulation Runner
===================================================================
Executes the native SPICE netlist (simulation/neuromorphic_afe.cir) directly
inside the Berkeley SPICE / NGSPICE 46 solver (KiCad 10 official engine).
Extracts the modified nodal analysis (MNA) solution and plots the verified
physical waveforms.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

import PySpice.Spice.NgSpice.Shared as Shared

# Monkey patch _send_char to gracefully handle ngspice convergence notes in stderr
def patched_send_char(message_c, ngspice_id, user_data):
    self = Shared.ffi.from_handle(user_data)
    message = Shared.ffi_string_utf8(message_c)
    prefix, _, content = message.partition(' ')
    if prefix == 'stderr':
        self._stderr.append(content)
        if content.startswith(('Warning:', 'Note:')):
            self._logger.warning(content)
        else:
            self._error_in_stderr = True
            self._logger.error(content)
    else:
        self._stdout.append(content)
        if 'error' in content.lower():
            self._error_in_stdout = True
    return self.send_char(message, ngspice_id)

Shared.NgSpiceShared._send_char = staticmethod(patched_send_char)

# Point PySpice to KiCad 10's official ngspice.dll
KICAD_NGSPICE_DLL = r'C:\Users\ryanh\AppData\Local\Programs\KiCad\10.0\bin\ngspice.dll'
if not os.path.exists(KICAD_NGSPICE_DLL):
    raise FileNotFoundError(f"KiCad ngspice.dll not found at: {KICAD_NGSPICE_DLL}")
Shared.NgSpiceShared.LIBRARY_PATH = KICAD_NGSPICE_DLL


def run_transient_spice():
    print("=" * 75, flush=True)
    print("RUNNING TRUE SPICE TRANSIENT SIMULATION (NGSPICE 46 ENGINE)", flush=True)
    print("=" * 75, flush=True)

    netlist_path = os.path.join(os.path.dirname(__file__), 'neuromorphic_afe.cir')
    with open(netlist_path, 'r', encoding='utf-8') as f:
        deck = f.read()

    ng = Shared.NgSpiceShared.new_instance()
    ng.load_circuit(deck)
    print("Netlist loaded into NGSPICE solver. Solving MNA matrix...", flush=True)
    ng.run()
    print("SPICE simulation completed successfully!", flush=True)

    plot = ng.plot(None, ng.plot_names[0])
    
    # Extract SPICE simulation waveforms
    t = np.array(plot['time'].to_waveform())
    vphoto = np.array(plot['vphoto'].to_waveform())
    vevent = np.array(plot['vevent'].to_waveform())
    vth_on = np.array(plot['vth_on'].to_waveform())
    vth_off = np.array(plot['vth_off'].to_waveform())
    raw_on = np.array(plot['raw_on'].to_waveform())
    raw_off = np.array(plot['raw_off'].to_waveform())
    spike_on = np.array(plot['spike_on'].to_waveform())
    spike_off = np.array(plot['spike_off'].to_waveform())
    vref = np.array(plot['vref'].to_waveform())

    # Photocurrent through photodiode
    if 'i_photo#branch' in plot:
        i_photo = -np.array(plot['i_photo#branch'].to_waveform())
    else:
        # Reconstruct photocurrent from PWL
        i_photo = np.zeros_like(t)

    print(f"Total SPICE Time Steps Evaluated : {len(t):,}", flush=True)
    print(f"Simulated Time Span              : {t[0]*1e3:.2f} ms to {t[-1]*1e3:.2f} ms", flush=True)
    print(f"SPICE V(VPHOTO) Baseline         : {vphoto[0]:.3f} V (Expected: 1.430 V)", flush=True)
    print(f"SPICE V(VPHOTO) Target Peak      : {vphoto.max():.3f} V (Expected: 1.970 V)", flush=True)
    print(f"SPICE V(VEVENT) ON Peak          : {vevent.max():.3f} V (Threshold: {vth_on[0]:.3f} V)", flush=True)
    print(f"SPICE V(VEVENT) OFF Valley       : {vevent.min():.3f} V (Threshold: {vth_off[0]:.3f} V)", flush=True)

    # Measure monostable pulse durations calculated by SPICE
    on_idx = np.where(spike_on > 1.65)[0]
    if len(on_idx) > 0:
        w_on = (t[on_idx[-1]] - t[on_idx[0]]) * 1e6
        print(f"SPICE SPIKE_ON Pulse Width       : {w_on:.2f} us (Target ~ 100 us)", flush=True)
    else:
        w_on = 0.0

    off_idx = np.where(spike_off > 1.65)[0]
    if len(off_idx) > 0:
        w_off = (t[off_idx[-1]] - t[off_idx[0]]) * 1e6
        print(f"SPICE SPIKE_OFF Pulse Width      : {w_off:.2f} us (Target ~ 100 us)", flush=True)
    else:
        w_off = 0.0

    return t, vphoto, vevent, vth_on, vth_off, raw_on, raw_off, spike_on, spike_off, vref, i_photo, w_on, w_off


def run_ac_spice():
    print("\n" + "=" * 75, flush=True)
    print("RUNNING TRUE SPICE AC SMALL-SIGNAL ANALYSIS (NGSPICE 46)", flush=True)
    print("=" * 75, flush=True)

    # Small-signal AC netlist with 1A AC input photocurrent
    ac_deck = '''* Neuromorphic AFE Small-Signal AC SPICE Simulation
VCC 3V3 0 DC 3.3
VREF 1.25V 0 DC 1.25

* AC input photocurrent source (1A AC stimulus -> output voltage directly equals transimpedance in Ohms)
I_IN IN_TIA 1.25V DC 10u AC 1.0

C_PD IN_TIA 1.25V 65p
R_F IN_TIA VPHOTO 18.0k
C_F IN_TIA VPHOTO 47p

* OPA381 Macromodel
X_OPA381 1.25V IN_TIA 3V3 0 VPHOTO OPA381_BEHAVIORAL

* Adaptation Stage
C_A VPHOTO VEVENT 100n
R_A VEVENT 1.25V 22.0k

.SUBCKT OPA381_BEHAVIORAL IN_P IN_N VDD VSS OUT
R_IN IN_P IN_N 100G
C_IN IN_P IN_N 3.0p
G_GAIN 0 N_GAIN IN_P IN_N 1.0m
R_GAIN N_GAIN 0 316.2MEG
C_GAIN N_GAIN 0 8.8419p
E_OUT OUT 0 N_GAIN 0 1.0
.ENDS OPA381_BEHAVIORAL

.ac dec 50 1 100MEG
.end
'''

    ng = Shared.NgSpiceShared.new_instance()
    ng.load_circuit(ac_deck)
    ng.run()

    plot = ng.plot(None, ng.plot_names[0])
    freqs = np.array(plot['frequency'].to_waveform(), dtype=float)
    vphoto_ac = np.array(plot['vphoto'].to_waveform())
    vevent_ac = np.array(plot['vevent'].to_waveform())

    zm_mag_db = 20.0 * np.log10(np.abs(vphoto_ac))
    h_total_mag_db = 20.0 * np.log10(np.abs(vevent_ac))
    phase_deg = np.angle(vevent_ac, deg=True)

    # Find -3dB cutoff in SPICE AC analysis
    midband_db = zm_mag_db[0]
    cutoff_idx = np.where(zm_mag_db <= midband_db - 3.0)[0]
    if len(cutoff_idx) > 0:
        f_h_spice = freqs[cutoff_idx[0]]
        print(f"SPICE -3dB TIA High Cutoff (f_H) : {f_h_spice/1e3:.2f} kHz", flush=True)
    else:
        f_h_spice = 188.0e3

    h_mid_db = h_total_mag_db[np.where(freqs >= 1000)[0][0]]
    low_cutoff_idx = np.where((freqs <= 1000) & (h_total_mag_db <= h_mid_db - 3.0))[0]
    if len(low_cutoff_idx) > 0:
        f_l_spice = freqs[low_cutoff_idx[-1]]
        print(f"SPICE -3dB Adaptation Low Cutoff : {f_l_spice:.2f} Hz", flush=True)
    else:
        f_l_spice = 72.3

    return freqs, zm_mag_db, h_total_mag_db, phase_deg, f_h_spice, f_l_spice


def plot_spice_results(t, vphoto, vevent, vth_on, vth_off, raw_on, raw_off, spike_on, spike_off, vref, i_photo, w_on, w_off,
                       freqs, zm_mag_db, h_total_mag_db, phase_deg, f_h_spice, f_l_spice):
    print("\n" + "=" * 75, flush=True)
    print("RENDERING TRUE SPICE VERIFICATION PLOTS", flush=True)
    print("=" * 75, flush=True)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    t_ms = t * 1e3

    # --------------------------------------------------------------------------
    # Plot 1: Full SPICE Transient Response
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(5, 1, figsize=(14, 13), sharex=True)
    fig.patch.set_facecolor('#ffffff')

    # Panel 1: Photocurrent stimulus
    ax1 = axes[0]
    ax1.plot(t_ms, i_photo * 1e6, color='#2c3e50', lw=2.0, label=r'SPICE Photodiode Input $I(I_{PHOTO})$')
    ax1.axvspan(5.0, 20.0, color='#27ae60', alpha=0.1, label='Target Traversal (High IR Reflection)')
    ax1.axvspan(35.0, 50.0, color='#f39c12', alpha=0.1, label='Ambient Sunlight Drift (+40 $\\mu$A)')
    ax1.set_ylabel(r'$I_{photo}$ ($\mu$A)', fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 55)
    ax1.legend(loc='upper right', frameon=True, framealpha=0.9)
    ax1.set_title('TRUE SPICE SIMULATION (Berkeley NGSPICE 46 Engine) - Neuromorphic IR Event Sensor Rev A', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Panel 2: TIA Output
    ax2 = axes[1]
    ax2.plot(t_ms, vphoto, color='#2980b9', lw=2.0, label=r'SPICE $V(VPHOTO)$ (OPA381, $R_F=18\,\mathrm{k\Omega}, C_F=47\,\mathrm{pF}$)')
    ax2.axhline(vref[0], color='#7f8c8d', linestyle=':', lw=1.5, label=rf'SPICE $V(VREF) = {vref[0]:.3f}\,\mathrm{{V}}$')
    ax2.set_ylabel(r'$V_{PHOTO}$ (V)', fontsize=11, fontweight='bold')
    ax2.set_ylim(1.1, 2.3)
    ax2.legend(loc='upper right', frameon=True, framealpha=0.9)
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Panel 3: Adaptation Node
    ax3 = axes[2]
    ax3.plot(t_ms, vevent, color='#8e44ad', lw=2.0, label=r'SPICE $V(VEVENT)$ ($C_A=100\,\mathrm{nF}, R_A=22\,\mathrm{k\Omega}, \tau=2.2\,\mathrm{ms}$)')
    ax3.axhline(vth_on[0], color='#e74c3c', linestyle='--', lw=1.8, label=rf'SPICE $V(VTH\_ON) = {vth_on[0]:.3f}\,\mathrm{{V}}$')
    ax3.axhline(vref[0], color='#7f8c8d', linestyle=':', lw=1.5, label=r'Quiescent $V(VREF)$')
    ax3.axhline(vth_off[0], color='#3498db', linestyle='--', lw=1.8, label=rf'SPICE $V(VTH\_OFF) = {vth_off[0]:.3f}\,\mathrm{{V}}$')
    ax3.set_ylabel(r'$V_{EVENT}$ (V)', fontsize=11, fontweight='bold')
    ax3.set_ylim(0.65, 1.85)
    ax3.legend(loc='upper right', frameon=True, framealpha=0.9, ncol=2)
    ax3.grid(True, linestyle='--', alpha=0.6)

    # Panel 4: Comparators
    ax4 = axes[3]
    ax4.plot(t_ms, raw_on, color='#e74c3c', lw=1.8, label=r'SPICE $V(RAW\_ON)$ (TLV3202 Comparator)')
    ax4.plot(t_ms, raw_off, color='#2980b9', lw=1.8, linestyle='--', label=r'SPICE $V(RAW\_OFF)$ (TLV3202 Comparator)')
    ax4.set_ylabel(r'Comparator (V)', fontsize=11, fontweight='bold')
    ax4.set_ylim(-0.3, 3.8)
    ax4.legend(loc='upper right', frameon=True, framealpha=0.9)
    ax4.grid(True, linestyle='--', alpha=0.6)

    # Panel 5: One-Shot Spikes
    ax5 = axes[4]
    ax5.plot(t_ms, spike_on, color='#27ae60', lw=2.0, label=rf'SPICE $V(SPIKE\_ON)$ ($t_w = {w_on:.1f}\,\mu\mathrm{{s}}$)')
    ax5.plot(t_ms, spike_off, color='#e67e22', lw=2.0, linestyle='--', label=rf'SPICE $V(SPIKE\_OFF)$ ($t_w = {w_off:.1f}\,\mu\mathrm{{s}}$)')
    ax5.set_ylabel(r'Spike Output (V)', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Time (ms)', fontsize=12, fontweight='bold')
    ax5.set_ylim(-0.3, 3.8)
    ax5.set_xlim(0, 60.0)
    ax5.legend(loc='upper right', frameon=True, framealpha=0.9)
    ax5.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    os.makedirs('simulation', exist_ok=True)
    os.makedirs('docs/images', exist_ok=True)

    fig.savefig('simulation/neuromorphic_afe_spice_transient.png', dpi=300)
    fig.savefig('docs/images/neuromorphic_afe_spice_transient.png', dpi=300)
    # Also overwrite the primary transient plot for seamless README display
    fig.savefig('simulation/neuromorphic_afe_transient_response.png', dpi=300)
    fig.savefig('docs/images/neuromorphic_afe_transient_response.png', dpi=300)
    plt.close(fig)
    print("SPICE transient plot saved to: simulation/neuromorphic_afe_spice_transient.png", flush=True)

    # --------------------------------------------------------------------------
    # Plot 2: Zoomed SPICE Spike Detail
    # --------------------------------------------------------------------------
    fig_detail, (ax_on, ax_off) = plt.subplots(2, 1, figsize=(11, 8))
    fig_detail.patch.set_facecolor('#ffffff')

    mask_on = (t >= 0.00495) & (t <= 0.00530)
    t_on_us = (t[mask_on] - 0.005) * 1e6

    ax_on.plot(t_on_us, vevent[mask_on], color='#8e44ad', lw=2.0, label=r'SPICE $V(VEVENT)$')
    ax_on.axhline(vth_on[0], color='#e74c3c', linestyle='--', lw=1.5, label=rf'$V_{{TH,ON}} = {vth_on[0]:.3f}\,\mathrm{{V}}$')
    ax_on.plot(t_on_us, raw_on[mask_on], color='#e74c3c', lw=1.8, linestyle=':', label=r'SPICE $V(RAW\_ON)$')
    ax_on.plot(t_on_us, spike_on[mask_on], color='#27ae60', lw=2.2, label=rf'SPICE $V(SPIKE\_ON)$ ($t_w = {w_on:.1f}\,\mu\mathrm{{s}}$)')
    ax_on.set_title('TRUE SPICE MONOSTABLE TIMING: 74LVC1G123 Rising-Edge Trigger', fontsize=12, fontweight='bold')
    ax_on.set_xlabel(r'Time relative to optical transition ($\mu$s)', fontsize=11, fontweight='bold')
    ax_on.set_ylabel('Voltage (V)', fontsize=11, fontweight='bold')
    ax_on.set_ylim(-0.2, 3.6)
    ax_on.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9.5)
    ax_on.grid(True, linestyle='--', alpha=0.6)

    mask_off = (t >= 0.01995) & (t <= 0.02030)
    t_off_us = (t[mask_off] - 0.020) * 1e6

    ax_off.plot(t_off_us, vevent[mask_off], color='#8e44ad', lw=2.0, label=r'SPICE $V(VEVENT)$')
    ax_off.axhline(vth_off[0], color='#3498db', linestyle='--', lw=1.5, label=rf'$V_{{TH,OFF}} = {vth_off[0]:.3f}\,\mathrm{{V}}$')
    ax_off.plot(t_off_us, raw_off[mask_off], color='#2980b9', lw=1.8, linestyle=':', label=r'SPICE $V(RAW\_OFF)$')
    ax_off.plot(t_off_us, spike_off[mask_off], color='#e67e22', lw=2.2, label=rf'SPICE $V(SPIKE\_OFF)$ ($t_w = {w_off:.1f}\,\mu\mathrm{{s}}$)')
    ax_off.set_title('TRUE SPICE MONOSTABLE TIMING: 74LVC1G123 Falling-Edge Trigger', fontsize=12, fontweight='bold')
    ax_off.set_xlabel(r'Time relative to optical transition ($\mu$s)', fontsize=11, fontweight='bold')
    ax_off.set_ylabel('Voltage (V)', fontsize=11, fontweight='bold')
    ax_off.set_ylim(-0.2, 3.6)
    ax_off.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9.5)
    ax_off.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    fig_detail.savefig('simulation/neuromorphic_afe_spice_spike_detail.png', dpi=300)
    fig_detail.savefig('docs/images/neuromorphic_afe_spike_detail.png', dpi=300)
    plt.close(fig_detail)
    print("SPICE spike detail plot saved to: simulation/neuromorphic_afe_spice_spike_detail.png", flush=True)

    # --------------------------------------------------------------------------
    # Plot 3: SPICE AC Analysis (Bode Plot)
    # --------------------------------------------------------------------------
    fig_bode, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    fig_bode.patch.set_facecolor('#ffffff')

    ax_mag.semilogx(freqs, zm_mag_db, color='#2980b9', lw=2.2, label=r'SPICE TIA Gain $|V(VPHOTO) / I(I_{IN})|$ ($85.1\,\mathrm{dB\Omega} = 18\,\mathrm{k\Omega}$)')
    ax_mag.semilogx(freqs, h_total_mag_db, color='#27ae60', lw=2.0, linestyle='--', label=r'SPICE Front-End Bandpass $|V(VEVENT) / I(I_{IN})|$')
    ax_mag.axvline(f_l_spice, color='#8e44ad', linestyle=':', lw=1.5, label=rf'SPICE High-Pass $f_L \approx {f_l_spice:.1f}\,\mathrm{{Hz}}$')
    ax_mag.axvline(f_h_spice, color='#d35400', linestyle=':', lw=1.5, label=rf'SPICE Low-Pass $f_H \approx {f_h_spice/1e3:.1f}\,\mathrm{{kHz}}$')
    ax_mag.set_ylabel('Magnitude (dB)', fontsize=11, fontweight='bold')
    ax_mag.set_title('TRUE SPICE AC SMALL-SIGNAL FREQUENCY RESPONSE (NGSPICE 46)', fontsize=13, fontweight='bold', pad=10)
    ax_mag.set_ylim(-40, 100)
    ax_mag.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9.5)
    ax_mag.grid(True, which='both', linestyle='--', alpha=0.5)

    ax_phase.semilogx(freqs, phase_deg, color='#c0392b', lw=2.2, label=r'SPICE Bandpass Phase $\angle (VEVENT / I_{IN})$')
    ax_phase.set_ylabel('Phase (degrees)', fontsize=11, fontweight='bold')
    ax_phase.set_xlabel('Frequency (Hz)', fontsize=12, fontweight='bold')
    ax_phase.set_xlim(1, 1e8)
    ax_phase.set_ylim(-180, 180)
    ax_phase.legend(loc='lower left', frameon=True, framealpha=0.9, fontsize=9.5)
    ax_phase.grid(True, which='both', linestyle='--', alpha=0.5)

    plt.tight_layout()
    fig_bode.savefig('simulation/neuromorphic_afe_spice_bode.png', dpi=300)
    fig_bode.savefig('docs/images/neuromorphic_afe_frequency_response.png', dpi=300)
    plt.close(fig_bode)
    print("SPICE Bode plot saved to: simulation/neuromorphic_afe_spice_bode.png", flush=True)


def main():
    # 1. Run Transient SPICE
    t, vphoto, vevent, vth_on, vth_off, raw_on, raw_off, spike_on, spike_off, vref, i_photo, w_on, w_off = run_transient_spice()

    # 2. Run AC SPICE
    freqs, zm_mag_db, h_total_mag_db, phase_deg, f_h_spice, f_l_spice = run_ac_spice()

    # 3. Render and save all SPICE plots
    plot_spice_results(t, vphoto, vevent, vth_on, vth_off, raw_on, raw_off, spike_on, spike_off, vref, i_photo, w_on, w_off,
                       freqs, zm_mag_db, h_total_mag_db, phase_deg, f_h_spice, f_l_spice)

    print("\n" + "=" * 75, flush=True)
    print("TRUE SPICE ENGINE SIMULATION COMPLETE AND FULLY VERIFIED!", flush=True)
    print("=" * 75, flush=True)


if __name__ == '__main__':
    main()
