"""
Pi 5 + AI HAT Dashcam Enclosure -- V1
Dual Camera (Front + Rear) -- Car Mount Design

Designed for: Raspberry Pi 5 + AI HAT+ (Hailo-8L)
Cameras: 2x Raspberry Pi Camera Module v3 (integrated mounts)
GPS: u-blox NEO-6M breakout (38x26mm PCB with 25x25mm ceramic antenna)
Features: Snap-fit closure, 30mm fan, status LED, power button access
Print material: PETG recommended (heat + vibration resistant)

Rewritten from OpenJSCAD to CadQuery (Python).
Loadable by cadquery-server via show_object().
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Raspberry Pi 5 (official mechanical drawing) ---
PI_W = 85.0            # board length (official: 85mm)
PI_D = 56.0            # board width  (official: 56mm)
PI_PCB_H = 1.6         # PCB thickness
PI_MOUNT_HOLE = 2.75   # M2.5 mounting holes (clearance 2.8-3.0mm)

# Pi 5 mounting hole positions (from bottom-left corner of PCB)
# Official: (5.5, 5.5), (79.5, 5.5), (5.5, 50.5), (79.5, 50.5)
# Horizontal spacing: 74mm, Vertical spacing: 45mm
PI_HOLES = [
    (5.5, 5.5),
    (79.5, 5.5),
    (5.5, 50.5),
    (79.5, 50.5),
]

# --- AI HAT+ ---
HAT_H = 5.5            # HAT PCB + components height
STACKING_H = 16        # stacking header height between Pi and HAT

# --- Camera Module v3 ---
CAM_W = 25             # camera board width
CAM_D = 24             # camera board depth
CAM_H = 11.5           # camera module total height
LENS_DIA = 8           # lens barrel diameter
LENS_PROTRUSION = 5    # how far the lens sticks out
CAM_MOUNT_HOLE = 2.0   # M2 camera mount screw diameter
CAM_HOLE_SPACING_W = 21    # horizontal hole center-to-center
CAM_HOLE_SPACING_H = 12.5  # vertical hole center-to-center

# --- GPS Module (u-blox NEO-6M breakout board, e.g. GY-GPS6MV2) ---
# Actual breakout PCB: 38 x 26 x 8.5mm (not just the 25x25 antenna)
GPS_W = 26             # board width
GPS_D = 38             # board length
GPS_H = 8.5            # board height including antenna
GPS_MOUNT_HOLE = 3.0   # M3 (common breakout board hole size)

# --- 30mm Fan ---
FAN_SIZE = 30
FAN_H = 10
FAN_MOUNT_HOLE = 3.2   # M3
FAN_HOLE_SPACING = 24  # center-to-center distance between mount holes

# --- Case construction ---
WALL = 2.5             # wall thickness (thicker for car vibration)
CORNER_R = 3           # fillet radius on outer edges
TOL = 0.4              # fit tolerance

# Internal stack height:
# standoffs(5) + Pi PCB(1.6) + under-board(3.5) + cooler(15) +
# stacking header(16) + HAT(5.5) + clearance(3)
INTERNAL_H = 50

# Internal cavity dimensions
INT_W = PI_W + TOL * 2
INT_D = PI_D + TOL * 2

# Camera housing that protrudes from case
CAM_HOUSING_W = CAM_W + WALL * 2 + 4   # ~33mm wide
CAM_HOUSING_H = CAM_D + WALL * 2 + 4   # ~32mm tall
CAM_HOUSING_DEPTH = CAM_H + WALL + 4   # ~18mm deep — sticks out from case
CAM_ANGLE = 15         # degrees downward tilt for road view

# External dimensions (main box only — camera housings protrude separately)
EXT_W = INT_W + WALL * 2
EXT_D = INT_D + WALL * 2
EXT_H = INTERNAL_H + WALL * 2
SPLIT_H = EXT_H / 2   # case splits in half horizontally

# --- Snap-fit tabs ---
SNAP_W = 12
SNAP_H = 3
SNAP_DEPTH = 1.5
SNAP_POSITIONS = [-25, 0, 25]  # X positions along each long side

# --- Windshield mount ---
MOUNT_W = 50
MOUNT_D = 35
MOUNT_H = 4
MOUNT_SLOT_W = 30
MOUNT_SLOT_D = 4

# --- Indicators and buttons ---
LED_DIA = 3            # recording LED diameter
PWR_BTN_DIA = 7        # power button hole diameter
STATUS_LED_W = 8       # status LED window width
STATUS_LED_H = 3       # status LED window height

# --- Cable routing ---
CABLE_CHAN_W = 10
CABLE_CHAN_H = 8

# --- microSD ---
SD_SLOT_W = 14
SD_SLOT_H = 3

# --- Ventilation grid parameters ---
VENT_SLOT_W = 2
VENT_SLOT_L = 5
VENT_GAP = 3.5
VENT_ROWS = 6

# --- Quarter-twenty threaded insert ---
QUARTER_TWENTY_DIA = 6.2  # hole for press-fit 1/4-20 insert

# --- Standoff dimensions ---
STANDOFF_H = 5         # height of Pi mounting standoffs
STANDOFF_OUTER_R = 3   # outer radius of standoff posts


# =============================================================================
# HELPER: Ventilation grid as a cuttable solid
# =============================================================================

def make_vent_grid(count_x, count_y, slot_w, slot_l, gap_x, gap_y, depth):
    """
    Create a grid of rectangular slots suitable for boolean subtraction.
    Returns a single CadQuery solid centered at the origin.
    """
    result = None
    start_x = -(count_x * (slot_w + gap_x) - gap_x) / 2
    start_y = -(count_y * (slot_l + gap_y) - gap_y) / 2

    for i in range(count_x):
        for j in range(count_y):
            cx = start_x + i * (slot_w + gap_x) + slot_w / 2
            cy = start_y + j * (slot_l + gap_y) + slot_l / 2
            slot = (
                cq.Workplane("XY")
                .center(cx, cy)
                .box(slot_w, slot_l, depth + 2, centered=True)
            )
            if result is None:
                result = slot
            else:
                result = result.union(slot)
    return result


# =============================================================================
# CAMERA HOUSING (protruding from front/rear face)
# =============================================================================

def build_camera_housing(side="front"):
    """
    Build a protruding camera housing that attaches to the case face.
    The housing tilts 15deg downward and has:
    - Camera module cavity
    - Lens aperture hole
    - M2 screw holes for camera board
    - CSI ribbon cable slot at the base
    """
    # Outer housing block
    housing = (
        cq.Workplane("XY")
        .box(CAM_HOUSING_W, CAM_HOUSING_DEPTH, CAM_HOUSING_H, centered=True)
    )
    # Fillet vertical edges for a cleaner look
    housing = housing.edges("|Z").fillet(2)

    # Camera module cavity (inside the housing)
    cam_cavity = (
        cq.Workplane("XY")
        .box(CAM_W + TOL * 2, CAM_H + TOL, CAM_D + TOL * 2, centered=True)
    )
    housing = housing.cut(cam_cavity)

    # Lens aperture through the outer face
    lens_hole = (
        cq.Workplane("XZ")
        .workplane(offset=CAM_HOUSING_DEPTH / 2)
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(WALL * 2)
    )
    housing = housing.cut(lens_hole)

    # M2 screw holes for camera board mounting (4 corners)
    for dx in [-CAM_HOLE_SPACING_W / 2, CAM_HOLE_SPACING_W / 2]:
        for dz in [-CAM_HOLE_SPACING_H / 2, CAM_HOLE_SPACING_H / 2]:
            m2_hole = (
                cq.Workplane("XZ")
                .center(dx, dz)
                .workplane(offset=-(CAM_HOUSING_DEPTH / 2))
                .circle(CAM_MOUNT_HOLE / 2)
                .extrude(-(CAM_HOUSING_DEPTH))
            )
            housing = housing.cut(m2_hole)

    # CSI ribbon cable slot at the back of the housing
    ribbon_slot = (
        cq.Workplane("XZ")
        .workplane(offset=-(CAM_HOUSING_DEPTH / 2))
        .rect(17, 3)
        .extrude(-(WALL * 2))
    )
    housing = housing.cut(ribbon_slot)

    # --- Position and angle the housing ---
    # Tilt downward by CAM_ANGLE degrees
    housing = housing.rotateAboutCenter((1, 0, 0), -CAM_ANGLE)

    if side == "front":
        # Attach to front face (+Y), centered vertically at mid-height
        housing = housing.translate((
            0,
            EXT_D / 2 + CAM_HOUSING_DEPTH / 2 - 2,  # protrude from front face
            SPLIT_H / 2 - 2   # vertically centered in bottom half
        ))
    else:
        # Rear camera: rotate 180deg around Z then position on -Y face
        housing = housing.rotateAboutCenter((0, 0, 1), 180)
        housing = housing.translate((
            0,
            -(EXT_D / 2 + CAM_HOUSING_DEPTH / 2 - 2),
            SPLIT_H / 2 - 2
        ))

    return housing


# =============================================================================
# BOTTOM HALF
# =============================================================================

def build_bottom_half():
    """
    Bottom half of the snap-fit enclosure.
    Contains: Pi mounting posts, USB-C / microSD / power button / LED cutouts,
    side ventilation, snap-fit ledge rim, and CSI ribbon cable passthrough
    slots in front/rear walls.
    Camera housings are added as separate protruding parts.
    """

    # --- Outer shell (rounded box, bottom half height) ---
    outer = (
        cq.Workplane("XY")
        .box(EXT_W, EXT_D, SPLIT_H, centered=True)
    )
    outer = outer.edges("|Z").fillet(CORNER_R)

    # --- Inner cavity ---
    cavity = (
        cq.Workplane("XY")
        .center(0, 0)
        .workplane(offset=WALL - SPLIT_H / 2)
        .box(INT_W, INT_D, SPLIT_H, centered=[True, True, False])
    )
    bottom = outer.cut(cavity)

    # -------------------------------------------------------------------------
    # CSI RIBBON CABLE PASSTHROUGH (slots in front and rear walls)
    # -------------------------------------------------------------------------

    # Front wall CSI slot
    csi_front = (
        cq.Workplane("XY")
        .center(12, EXT_D / 2)
        .workplane(offset=WALL + 2 - SPLIT_H / 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    bottom = bottom.cut(csi_front)

    # Rear wall CSI slot
    csi_rear = (
        cq.Workplane("XY")
        .center(-12, -(EXT_D / 2))
        .workplane(offset=WALL + 2 - SPLIT_H / 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    bottom = bottom.cut(csi_rear)

    # -------------------------------------------------------------------------
    # PORT CUTOUTS
    # Pi 5 orientation: USB-C/HDMI on left short wall (-X), microSD on
    # right short wall (+X), USB 3.0/Ethernet on rear long wall (-Y, blocked
    # by case — dashcam doesn't need network ports).
    # -------------------------------------------------------------------------

    # USB-C power port (left short wall, -X face)
    # Pi 5 USB-C: ~9mm wide x 3.2mm tall connector, centered ~11.2mm from
    # bottom edge of the 56mm side. With standoffs (5mm) + PCB (1.6mm),
    # the connector center is at ~WALL + 5 + 1.6 + 1.6 = ~10mm up from floor.
    # Add extra clearance for connector housing: 12mm wide x 8mm tall cutout.
    usbc = (
        cq.Workplane("YZ")
        .workplane(offset=-(EXT_W / 2 + 1))
        .center(-(INT_D / 2) + 11.2, WALL + STANDOFF_H + PI_PCB_H + 1.6 - SPLIT_H / 2)
        .rect(12, 8)
        .extrude(WALL + 2)
    )
    bottom = bottom.cut(usbc)

    # Cable routing channel (below USB-C, for hardwired 12V-to-USB-C cable)
    cable_chan = (
        cq.Workplane("YZ")
        .workplane(offset=-(EXT_W / 2 + 1))
        .center(-(INT_D / 2) + 11.2, WALL + 2 - SPLIT_H / 2)
        .rect(CABLE_CHAN_W, CABLE_CHAN_H)
        .extrude(WALL + 2)
    )
    bottom = bottom.cut(cable_chan)

    # 2x micro HDMI ports (left short wall, above USB-C)
    # Pi 5 has two micro HDMI ports on the same edge as USB-C.
    # HDMI0 center ~26mm from bottom, HDMI1 center ~39.5mm from bottom
    # of the 56mm edge. Each micro HDMI connector: ~7mm wide x 3mm tall.
    for hdmi_y_offset in [26.0, 39.5]:
        hdmi = (
            cq.Workplane("YZ")
            .workplane(offset=-(EXT_W / 2 + 1))
            .center(-(INT_D / 2) + hdmi_y_offset,
                    WALL + STANDOFF_H + PI_PCB_H + 1.6 - SPLIT_H / 2)
            .rect(8, 4)
            .extrude(WALL + 2)
        )
        bottom = bottom.cut(hdmi)

    # microSD card slot access (right short wall, +X face)
    # Pi 5 microSD is on the opposite short edge, spring-loaded slot.
    # Roughly centered on the 56mm side at ~28mm from bottom edge.
    # Slot opening: ~14mm wide x 3mm tall.
    sd_slot = (
        cq.Workplane("YZ")
        .workplane(offset=EXT_W / 2 - WALL)
        .center(0, WALL + 2 - SPLIT_H / 2)
        .rect(SD_SLOT_W, SD_SLOT_H)
        .extrude(WALL + 2)
    )
    bottom = bottom.cut(sd_slot)

    # -------------------------------------------------------------------------
    # BUTTON AND LED CUTOUTS
    # -------------------------------------------------------------------------

    # Power button access hole
    # Pi 5 power button is on the PCB top surface near the microSD edge
    # (right short wall, +X side), about 3mm from the GPIO-side long edge.
    # We cut a hole through the right wall for a poking tool / extension.
    pwr_btn = (
        cq.Workplane("YZ")
        .workplane(offset=EXT_W / 2 - WALL)
        .center(INT_D / 2 - 5,
                WALL + STANDOFF_H + PI_PCB_H + 3 - SPLIT_H / 2)
        .circle(PWR_BTN_DIA / 2)
        .extrude(WALL + 2)
    )
    bottom = bottom.cut(pwr_btn)

    # Pi 5 activity LED window (on PCB surface, visible through case)
    # LED is near the USB-C end. Window on left short wall.
    status_led = (
        cq.Workplane("YZ")
        .workplane(offset=-(EXT_W / 2 + 1))
        .center(-(INT_D / 2) + 3,
                WALL + STANDOFF_H + PI_PCB_H + 2 - SPLIT_H / 2)
        .rect(STATUS_LED_W, STATUS_LED_H)
        .extrude(WALL + 2)
    )
    bottom = bottom.cut(status_led)

    # Recording indicator LED (front face — visible from outside the car)
    rec_led = (
        cq.Workplane("XZ")
        .center(15, 10 - SPLIT_H / 2)
        .workplane(offset=EXT_D / 2)
        .circle(LED_DIA / 2)
        .extrude(WALL * 3)
    )
    bottom = bottom.cut(rec_led)

    # -------------------------------------------------------------------------
    # SIDE VENTILATION GRIDS
    # -------------------------------------------------------------------------

    vent_grid = make_vent_grid(1, VENT_ROWS, VENT_SLOT_W, VENT_SLOT_L, 0, VENT_GAP, WALL)

    left_vents = vent_grid.translate((-(EXT_W / 2), 0, -2))
    left_vents = left_vents.rotateAboutCenter((0, 1, 0), 90)
    bottom = bottom.cut(left_vents)

    right_vents = vent_grid.translate((EXT_W / 2, 0, -2))
    right_vents = right_vents.rotateAboutCenter((0, 1, 0), 90)
    bottom = bottom.cut(right_vents)

    # -------------------------------------------------------------------------
    # Pi 5 MOUNTING POSTS (5mm standoffs from floor)
    # -------------------------------------------------------------------------

    for hx, hy in PI_HOLES:
        px = hx - INT_W / 2 + TOL
        py = hy - INT_D / 2 + TOL
        pz = -(SPLIT_H / 2) + WALL

        standoff = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=pz)
            .circle(STANDOFF_OUTER_R)
            .extrude(STANDOFF_H)
        )
        screw_hole = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=pz - 0.5)
            .circle(PI_MOUNT_HOLE / 2)
            .extrude(STANDOFF_H + 1)
        )
        post = standoff.cut(screw_hole)
        bottom = bottom.union(post)

    # -------------------------------------------------------------------------
    # SNAP-FIT LEDGE (rim for top half to sit on)
    # -------------------------------------------------------------------------

    snap_ledge_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 2)
        .box(INT_W + 2, INT_D + 2, 2, centered=[True, True, False])
    )
    snap_ledge_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 2.5)
        .box(INT_W - 2, INT_D - 2, 3, centered=[True, True, False])
    )
    snap_ledge = snap_ledge_outer.cut(snap_ledge_inner)
    bottom = bottom.union(snap_ledge)

    # -------------------------------------------------------------------------
    # PROTRUDING CAMERA HOUSINGS (front + rear)
    # -------------------------------------------------------------------------

    front_cam = build_camera_housing("front")
    rear_cam = build_camera_housing("rear")
    bottom = bottom.union(front_cam)
    bottom = bottom.union(rear_cam)

    # Move bottom half so its base sits at Z=0 (build plate)
    bottom = bottom.translate((0, 0, SPLIT_H / 2))

    return bottom


# =============================================================================
# TOP HALF (LID)
# =============================================================================

def build_top_half():
    """
    Top half / lid of the snap-fit enclosure.
    Contains: 30mm fan mount with screw holes, GPS module recess with thinned
    antenna window, snap-fit inner rim + tabs, windshield mount tab with
    adhesive slot, and 1/4-20 threaded insert hole.
    """

    # --- Outer shell ---
    outer = (
        cq.Workplane("XY")
        .box(EXT_W, EXT_D, SPLIT_H, centered=True)
    )
    outer = outer.edges("|Z").fillet(CORNER_R)

    # --- Inner cavity (hollowed from below, leaving WALL on top) ---
    cavity = (
        cq.Workplane("XY")
        .center(0, 0)
        .workplane(offset=SPLIT_H / 2 - WALL)
        .box(INT_W, INT_D, SPLIT_H, centered=[True, True, False])
        .translate((0, 0, -(SPLIT_H)))
    )
    top = outer.cut(cavity)

    # -------------------------------------------------------------------------
    # 30mm FAN MOUNT (centered on top, directly over AI HAT)
    # -------------------------------------------------------------------------

    # Main fan intake hole
    fan_hole = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2)
        .circle(FAN_SIZE / 2 - 2)
        .extrude(-(WALL * 3))
    )
    top = top.cut(fan_hole)

    # Fan M3 screw holes
    for fx in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
        for fy in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
            screw = (
                cq.Workplane("XY")
                .center(fx, fy)
                .workplane(offset=SPLIT_H / 2)
                .circle(FAN_MOUNT_HOLE / 2)
                .extrude(-(WALL * 3))
            )
            top = top.cut(screw)

    # Fan intake ventilation grid around the fan opening
    fan_vent_grid = make_vent_grid(4, 4, 2, 3, 4, 4, WALL)
    fan_vents = fan_vent_grid.translate((0, 0, SPLIT_H / 2))
    top = top.cut(fan_vents)

    # -------------------------------------------------------------------------
    # GPS MODULE RECESS (top surface, offset from fan)
    # -------------------------------------------------------------------------

    gps_recess = (
        cq.Workplane("XY")
        .center(-(EXT_W / 4), 0)
        .workplane(offset=SPLIT_H / 2 - GPS_H / 2)
        .box(GPS_W + TOL * 2, GPS_D + TOL * 2, GPS_H + 1, centered=True)
    )
    top = top.cut(gps_recess)

    # Thinned antenna window
    gps_window = (
        cq.Workplane("XY")
        .center(-(EXT_W / 4), 0)
        .workplane(offset=SPLIT_H / 2)
        .box(GPS_W - 4, GPS_D - 4, WALL, centered=True)
    )
    top = top.cut(gps_window)

    # GPS M3 mount holes
    for gx in [-(GPS_W / 2 - 2), (GPS_W / 2 - 2)]:
        for gy in [-(GPS_D / 2 - 2), (GPS_D / 2 - 2)]:
            gps_hole = (
                cq.Workplane("XY")
                .center(gx - EXT_W / 4, gy)
                .workplane(offset=SPLIT_H / 2 - GPS_H)
                .circle(GPS_MOUNT_HOLE / 2)
                .extrude(GPS_H + WALL + 2)
            )
            top = top.cut(gps_hole)

    # -------------------------------------------------------------------------
    # SNAP-FIT INNER RIM + TABS
    # -------------------------------------------------------------------------

    snap_rim_outer = (
        cq.Workplane("XY")
        .workplane(offset=-(SPLIT_H / 2) + 1)
        .box(INT_W, INT_D, 2.5, centered=True)
    )
    snap_rim_inner = (
        cq.Workplane("XY")
        .workplane(offset=-(SPLIT_H / 2) + 1)
        .box(INT_W - 3, INT_D - 3, 3.5, centered=True)
    )
    snap_rim = snap_rim_outer.cut(snap_rim_inner)
    top = top.union(snap_rim)

    for xpos in SNAP_POSITIONS:
        tab_front = (
            cq.Workplane("XY")
            .center(xpos, INT_D / 2)
            .workplane(offset=-(SPLIT_H / 2) + 1)
            .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
        )
        top = top.union(tab_front)

        tab_rear = (
            cq.Workplane("XY")
            .center(xpos, -(INT_D / 2))
            .workplane(offset=-(SPLIT_H / 2) + 1)
            .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
        )
        top = top.union(tab_rear)

    # -------------------------------------------------------------------------
    # WINDSHIELD MOUNT TAB (on top surface)
    # -------------------------------------------------------------------------

    mount_base = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 0.5)
        .box(MOUNT_W, MOUNT_D, MOUNT_H, centered=[True, True, False])
    )
    mount_base = mount_base.edges("|Z").fillet(2)
    top = top.union(mount_base)

    # Adhesive pad / suction cup slot
    mount_slot = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 + MOUNT_H / 2 - 0.5)
        .box(MOUNT_SLOT_W, MOUNT_SLOT_D, MOUNT_H + 2, centered=True)
    )
    top = top.cut(mount_slot)

    # 1/4-20 threaded insert hole
    quarter_twenty = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2)
        .circle(QUARTER_TWENTY_DIA / 2)
        .extrude(-(MOUNT_H + WALL + 2))
    )
    top = top.cut(quarter_twenty)

    # Position top half above bottom for assembly preview
    top = top.translate((0, 0, SPLIT_H + SPLIT_H / 2 + 0.5))

    return top


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

bottom_half = build_bottom_half()
top_half = build_top_half()

show_object(bottom_half, name="bottom_half", options={"color": (0.15, 0.15, 0.15, 0.9)})
show_object(top_half, name="top_half", options={"color": (0.25, 0.25, 0.25, 0.85)})
