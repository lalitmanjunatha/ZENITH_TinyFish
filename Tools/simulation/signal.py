"""
ZENITH Signal Processing Module
Implements: Fourier Transform, FFT, Convolution, Filter Design, Sampling Theorem
"""

import math
import numpy as np
from typing import Any, Dict
from .core import BaseSimulation, VisHelper, get_engine

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as _np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class FourierTransformSim(BaseSimulation):
    SIM_TYPE = "fourier_transform"
    SIM_NAME = "Fourier Transform"

    def __init__(self, params=None):
        defaults = {
            "signal_type": "composite",
            "frequencies": [5, 15, 30],
            "amplitudes": [1.0, 0.5, 0.3],
            "duration": 1.0,
            "sample_rate": 500,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY:
            return
        sr = self.params["sample_rate"]
        dur = self.params["duration"]
        self.t = np.linspace(0, dur, int(sr * dur))
        self.signal = np.zeros_like(self.t)
        for f, a in zip(self.params["frequencies"], self.params["amplitudes"]):
            self.signal += a * np.sin(2 * np.pi * f * self.t)

        # Compute FFT
        N = len(self.signal)
        self.fft_vals = np.fft.fft(self.signal)
        self.freqs = np.fft.fftfreq(N, 1 / sr)
        self.magnitude = np.abs(self.fft_vals) / N
        self.phase = np.angle(self.fft_vals)
        self.metrics = {"dominant_freq": self.params["frequencies"][0], "num_components": len(self.params["frequencies"])}

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        # Time domain
        ax = axes[0][0]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.t[:200], self.signal[:200], color=vis.COLORS["cyan"], linewidth=1.5)
        ax.set_title("Time Domain Signal", color='white', fontsize=12)
        vis.label_axes(ax, "Time (s)", "Amplitude")
        vis.add_grid(ax)

        # Frequency domain (magnitude)
        ax = axes[0][1]; ax.set_facecolor('#0a0a0f')
        pos_mask = self.freqs > 0
        ax.plot(self.freqs[pos_mask], self.magnitude[pos_mask], color=vis.COLORS["orange"], linewidth=1.5)
        ax.set_title("Frequency Spectrum (Magnitude)", color='white', fontsize=12)
        vis.label_axes(ax, "Frequency (Hz)", "Magnitude")
        vis.add_grid(ax)

        # Phase spectrum
        ax = axes[1][0]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.freqs[pos_mask], self.phase[pos_mask], color=vis.COLORS["green"], linewidth=1)
        ax.set_title("Phase Spectrum", color='white', fontsize=12)
        vis.label_axes(ax, "Frequency (Hz)", "Phase (rad)")
        vis.add_grid(ax)

        # FFT bins (bar)
        ax = axes[1][1]; ax.set_facecolor('#0a0a0f')
        peak_freqs = self.params["frequencies"]
        peak_amps = self.params["amplitudes"]
        ax.bar(peak_freqs, peak_amps, color=vis.COLORS["purple"], width=3, alpha=0.7)
        ax.set_title("Detected Frequencies", color='white', fontsize=12)
        vis.label_axes(ax, "Frequency (Hz)", "Amplitude")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"fourier_{int(self.time*1000)}.png", output_dir)

    def explain(self):
        return (f"Fourier Transform: Decomposed signal into {len(self.params['frequencies'])} frequency components\n"
                f"Frequencies: {self.params['frequencies']} Hz\n"
                f"Amplitudes: {self.params['amplitudes']}")


class ConvolutionSim(BaseSimulation):
    SIM_TYPE = "convolution"
    SIM_NAME = "Convolution Operation"

    def __init__(self, params=None):
        defaults = {
            "signal": [0, 0, 1, 1, 1, 0, 0, 0, 2, 2, 0, 0],
            "kernel": [1, 2, 1],
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY:
            return
        sig = np.array(self.params["signal"], dtype=float)
        ker = np.array(self.params["kernel"], dtype=float)
        self.conv = np.convolve(sig, ker, mode='full')
        self.signal_padded = sig
        self.kernel_padded = ker

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.stem(range(len(self.signal_padded)), self.signal_padded, linefmt=vis.COLORS["cyan"],
               markerfmt='o', basefmt='gray')
        ax.set_title("Input Signal", color='white', fontsize=12)
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.stem(range(len(self.kernel_padded)), self.kernel_padded, linefmt=vis.COLORS["orange"],
               markerfmt='o', basefmt='gray')
        ax.set_title("Kernel", color='white', fontsize=12)
        vis.add_grid(ax)

        ax = axes[2]; ax.set_facecolor('#0a0a0f')
        ax.stem(range(len(self.conv)), self.conv, linefmt=vis.COLORS["green"],
               markerfmt='o', basefmt='gray')
        ax.set_title("Convolution Result", color='white', fontsize=12)
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"convolution_{int(self.time*1000)}.png", output_dir)


class FilterDesignSim(BaseSimulation):
    SIM_TYPE = "filter_design"
    SIM_NAME = "Digital Filter Design"

    def __init__(self, params=None):
        defaults = {
            "filter_type": "low_pass",
            "cutoff": 50,
            "sample_rate": 500,
            "order": 5,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY:
            return
        sr = self.params["sample_rate"]
        self.N = 256
        self.freqs = np.linspace(0, sr / 2, self.N // 2)
        cutoff = self.params["cutoff"]
        ft = self.params["filter_type"]

        if ft == "low_pass":
            self.response = 1 / (1 + (self.freqs / cutoff) ** (2 * self.params["order"]))
        elif ft == "high_pass":
            self.response = 1 - 1 / (1 + (self.freqs / cutoff) ** (2 * self.params["order"]))
        elif ft == "band_pass":
            low = cutoff * 0.7; high = cutoff * 1.3
            self.response = np.exp(-((self.freqs - cutoff) / (high - low)) ** 2)
        elif ft == "band_stop":
            low = cutoff * 0.7; high = cutoff * 1.3
            self.response = 1 - np.exp(-((self.freqs - cutoff) / (high - low)) ** 2)
        else:
            self.response = np.ones_like(self.freqs)

        self.phase_response = -np.arctan2(self.response, 1 - self.response)
        self.metrics = {"cutoff": cutoff, "filter_type": ft, "order": self.params["order"]}

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.freqs, 20 * np.log10(self.response + 1e-10), color=vis.COLORS["cyan"], linewidth=2)
        ax.axvline(x=self.params["cutoff"], color=vis.COLORS["yellow"], linestyle='--', alpha=0.5, label=f"Cutoff={self.params['cutoff']}Hz")
        ax.set_title(f"{self.params['filter_type'].replace('_', ' ').title()} Filter Response", color='white', fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Frequency (Hz)", "Magnitude (dB)")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.freqs, self.phase_response, color=vis.COLORS["orange"], linewidth=1.5)
        ax.set_title("Phase Response", color='white', fontsize=12)
        vis.label_axes(ax, "Frequency (Hz)", "Phase (rad)")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"filter_{self.params['filter_type']}_{int(self.time*1000)}.png", output_dir)


class SamplingTheoremSim(BaseSimulation):
    SIM_TYPE = "sampling_theorem"
    SIM_NAME = "Nyquist Sampling Theorem"

    def __init__(self, params=None):
        defaults = {
            "original_freq": 10,
            "sampling_rate": 30,
            "duration": 1.0,
        }
        p = {**defaults, **(params or {})}
        super().__init__(p)

    def initialize(self):
        super().initialize()
        if not HAS_NUMPY:
            return
        dur = self.params["duration"]
        f = self.params["original_freq"]
        sr = self.params["sampling_rate"]

        self.t_fine = np.linspace(0, dur, 1000)
        self.signal = np.sin(2 * np.pi * f * self.t_fine)

        self.t_sampled = np.arange(0, dur, 1 / sr)
        self.samples = np.sin(2 * np.pi * f * self.t_sampled)

        # Reconstructed via sinc interpolation
        self.signal_recon = np.zeros_like(self.t_fine)
        for i, s in enumerate(self.samples):
            self.signal_recon += s * np.sinc((self.t_fine - self.t_sampled[i]) * sr)

        nyquist_rate = 2 * f
        self.metrics = {
            "signal_freq": f, "sampling_rate": sr,
            "nyquist_rate": nyquist_rate,
            "undersampled": sr < nyquist_rate,
            "ratio": sr / nyquist_rate,
        }

    def step(self, dt=0.02):
        super().step(dt)

    def visualize(self, output_dir=None):
        if not HAS_MPL or not HAS_NUMPY:
            return "matplotlib/numpy not available"
        output_dir = output_dir or get_engine().output_dir
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0a0a0f')
        vis = VisHelper()

        ax = axes[0]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.t_fine, self.signal, color=vis.COLORS["cyan"], linewidth=1.5, label="Original", alpha=0.5)
        ax.plot(self.t_sampled, self.samples, 'o', color=vis.COLORS["red"], markersize=5, label="Samples")
        ax.set_title(f"Sampling at {self.params['sampling_rate']} Hz (Nyquist: {2*self.params['original_freq']} Hz)", color='white', fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Amplitude")
        vis.add_grid(ax)

        ax = axes[1]; ax.set_facecolor('#0a0a0f')
        ax.plot(self.t_fine, self.signal, color=vis.COLORS["cyan"], linewidth=1.5, label="Original", alpha=0.5)
        ax.plot(self.t_fine, self.signal_recon, color=vis.COLORS["green"], linewidth=1.5, label="Reconstructed")
        aliasing = "YES (Aliasing!)" if self.metrics["undersampled"] else "NO"
        color = vis.COLORS["red"] if self.metrics["undersampled"] else vis.COLORS["green"]
        ax.set_title(f"Reconstruction | Aliasing: {aliasing}", color=color, fontsize=12)
        ax.legend(fontsize=9, facecolor='#111827', edgecolor='#334155', labelcolor='white')
        vis.label_axes(ax, "Time (s)", "Amplitude")
        vis.add_grid(ax)

        plt.tight_layout()
        return VisHelper.save_figure(fig, f"sampling_{int(self.time*1000)}.png", output_dir)


def register_signal_simulations(engine=None):
    engine = engine or get_engine()
    engine.register_simulation("fourier_transform", FourierTransformSim)
    engine.register_simulation("convolution", ConvolutionSim)
    engine.register_simulation("filter_design", FilterDesignSim)
    engine.register_simulation("sampling_theorem", SamplingTheoremSim)
