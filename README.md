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
| `designs/v0-prototype.jscad` | Initial prototype with separate camera arms |
| `designs/v1-dashcam.jscad` | V1 — integrated cameras, snap-fit, fan, GPS |
| `stl/` | Exported STL files ready for slicing |

## V1 Features

- **Integrated camera mounts** — front and rear cameras angled 15deg downward, built into case walls
- **Snap-fit closure** — no screws needed to open/close
- **30mm fan mount** — centered over AI HAT for active cooling
- **GPS module recess** — top-mounted with thinned wall for antenna signal
- **1/4-20 mount** — standard dashcam/camera mount thread
- **Cable routing channel** — for hardwired 12V USB-C power
- **Status indicators** — recording LED (front), Pi activity LED window
- **Full port access** — USB-C power, microSD, power button
- **Ventilation** — side grids + fan intake

## Print Settings

- **Material:** PETG recommended (heat + vibration resistant)
- **Layer height:** 0.2mm
- **Infill:** 20-30%
- **Walls:** 3 perimeters minimum
- **Supports:** Yes, for camera pockets and overhangs

## Editing

Open `.jscad` files in [OpenJSCAD](https://openjscad.xyz) or our self-hosted instance.

## License

MIT
