# Pi 5 AI Dashcam Enclosure

3D printable enclosure for a Raspberry Pi 5 + AI HAT+ (Hailo-8L) dashcam with dual cameras and GPS.

## Hardware

- **Compute:** Raspberry Pi 5
- **AI:** Raspberry Pi AI HAT+ (Hailo-8L) for real-time detection
- **Cameras:** 2x Raspberry Pi Camera Module v3 (front + rear)
- **GPS:** u-blox NEO-6M/7M/8M module (25x25mm standard)
- **Cooling:** 30mm fan
- **Printer:** QIDI Q2

## Design Files

| File | Description |
|------|-------------|
| `designs/v0-prototype.py` | Simplified prototype — open-top tray for fit checks |
| `designs/v1-dashcam.py` | V1 — full snap-fit enclosure with all features |
| `designs/v2-dash-display.py` | V2 — ultra-wide 11.9" touchscreen bar with flush center cameras |
| `stl/` | Exported STL files ready for slicing |

Designs are written in **CadQuery** (Python) and rendered via [cadquery-server](https://github.com/robodk/cadquery-server). Open in any CadQuery-compatible viewer or our self-hosted instance.

## V1 Features

- **Snap-fit two-piece enclosure** — bottom tray + top lid with snap tabs, no screws needed
- **Integrated camera mounts** — front and rear cameras angled 15deg downward with M2 mounting holes
- **CSI ribbon cable channels** — routed from Pi to each camera pocket
- **30mm fan mount** — centered over AI HAT for active cooling with M3 screw holes
- **GPS module recess** — top-mounted (u-blox NEO 25x25mm) with thinned antenna window
- **1/4-20 mount** — standard dashcam/camera mount threaded insert hole
- **Cable routing channel** — for hardwired 12V USB-C power
- **Status indicators** — recording LED (front), Pi activity LED window
- **Full port access** — USB-C power, microSD, power button
- **Ventilation** — side grids + fan intake
- **2.5mm walls** — PETG, vibration resistant for vehicle use

## V2 Features (Dash Display)

- **Ultra-wide 11.9" touchscreen** — Waveshare 320x1480 capacitive DSI display
- **Flush center cameras** — front and rear cameras back-to-back at top-center, no protrusions
- **4-piece snap-fit enclosure** — left/right x top/bottom, prints on QIDI Q2 (270x270mm)
- **Wedge profile** — 9-degree tilt angles screen toward driver
- **Camera zone above display** — bar taller than screen to house flush-mounted cameras
- **Magnetic dash mount** — 4x neodymium magnets snap onto 3M-adhered steel plate
- **30mm fan mount** — rear-wall exhaust for active cooling of AI HAT+
- **GPS module recess** — top-mounted with thinned antenna window
- **Center seam joining** — tongue-and-groove + M3 screws for left/right alignment
- **Full port access** — USB-C power, microSD, power button
- **Internal CSI cable channels** — ribbon cables route vertically from camera zone to Pi

## Print Settings

- **Material:** PETG recommended (heat + vibration resistant)
- **Layer height:** 0.2mm
- **Infill:** 20-30%
- **Walls:** 3 perimeters minimum
- **Supports:** Yes, for camera pockets and overhangs

## Editing

Designs use [CadQuery](https://cadquery.readthedocs.io/) — a Python parametric CAD library backed by OpenCascade. All dimensions are defined as variables at the top of each file for easy customization.

```bash
# Run locally
pip install cadquery cadquery-server
cq-server /path/to/designs/

# Or use our self-hosted CadQuery Server instance
```

## License

MIT
