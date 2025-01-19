from config import *
from svgpathtools import svg2paths
import numpy as np
import xml.etree.ElementTree as ET

# Sample the points on the paths.
paths, attributes = svg2paths(INPUT_FILE_PATH)
samples = []
for path in paths:
    samples.extend(path.point(e) for e in np.linspace(0, 1, int(SAMPLE_MULTIPLE * path.length())))
sample_count = len(samples)

print(f"count of samples: {sample_count}")

# Preprocess the sampled points.
scale = np.abs(samples).max()
center = np.mean(samples)
samples = (np.array(samples) - center) / scale

# Compute amplitudes, frequencies, and phases using FFT.
coefficients = np.fft.fft(samples, norm="forward")
amplitudes = np.abs(coefficients)
frequencies = np.fft.fftfreq(sample_count, 1 / sample_count)
phases = np.angle(coefficients)

# Select the epicycles with the highest amplitudes.
epicycle_count = int(EPICYCLE_RATE * sample_count)
epicycles = sorted(zip(amplitudes, frequencies, phases), reverse=True)[:epicycle_count]

print(f"count of epicycles: {epicycle_count}")

# Resample the points from the epicycles.
resample_count = RESAMPLE_RATE * sample_count
resamples = [np.sum([a * np.exp(1j * (f * t + p)) for a, f, p in epicycles]) for t in np.linspace(0, 2 * np.pi, resample_count)]
# Use this when performing the exact IFFT.
# resamples = np.fft.ifft(coefficients, norm="forward")

print(f"count of resamples: {resample_count}")

# Create an SVG element and insert a group element that defines size, position, and style
svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg")
g = ET.SubElement(svg, "g", transform=f"translate({center.real} {center.imag}) scale({scale})", style=f"fill: none; stroke: black; stroke-width: {1 / scale}")

# Add the resampled points as line elements.
for i in range(resample_count):
    line = ET.SubElement(g, "line", x1=f"{resamples[i - 1].real}", y1=f"{resamples[i - 1].imag}", x2=f"{resamples[i].real}", y2=f"{resamples[i].imag}")
    ET.SubElement(line, "animate", attributeName="opacity", values=f"1; 0", dur=f"{ANIMATION_DURATION}s", begin=f"{ANIMATION_DURATION * (i - resample_count) / resample_count}", repeatCount="indefinite")
# Use this when you only need the path.
# ET.SubElement(g, "polygon", points=" ".join(f"{e.real} {e.imag}" for e in resamples))

# Add the Fourier epicycles as group elements.
prev_a = 1
prev_f = 0
prev_p = 0
prev_epicycle = g
for a, f, p in epicycles:
    f *= 360
    p *= 180 / np.pi
    if prev_epicycle == g:
        prev_epicycle = ET.SubElement(prev_epicycle, "g", transform=f"scale({a}) rotate({p})")
    else:
        prev_epicycle = ET.SubElement(prev_epicycle, "g", transform=f"translate(1 0) scale({a / prev_a}) rotate({p - prev_p})")
    ET.SubElement(prev_epicycle, "animateTransform", attributeName="transform", type="rotate", values=f"0; {f-prev_f}", dur=f"{ANIMATION_DURATION}s", repeatCount="indefinite", additive="sum")
    ET.SubElement(prev_epicycle, "circle", r="1")
    ET.SubElement(prev_epicycle, "line", x2="1")
    prev_a = a
    prev_f = f
    prev_p = p

# Create an XML tree with SVG as the root and save it to a file.
ET.ElementTree(svg).write(OUTPUT_FILE_PATH, encoding="utf-8")
