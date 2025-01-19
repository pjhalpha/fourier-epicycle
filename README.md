# Outline
The program that convert a SVG file to SVG paths with animation using Fourier epicycles.

# Features
This program samples points from `line`, `polyline`, `polygon`, and `path` SVG elements. After sampling, resampled points and Fourier epicycles with animation are saved as an SVG file.

# Prerequisites
To run the program, you need to install the `svgpathtools` and `numpy` packages. You can install them using pip with the following command:

```bash
pip install -r requirements
```

# Usage
Prepare a SVG file and modify the config.py if necessary. Then, run the `main.py`, and the converted SVG file will be generated.
