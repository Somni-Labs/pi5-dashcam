"""
Pi 5 + AI HAT Dash Display Enclosure -- V2.1
Ultra-wide 11.9" touchscreen bar with flush center cameras -- Dashboard mount

Designed for: Raspberry Pi 5 + AI HAT+ (Hailo-8L)
Display: Waveshare 11.9" DSI LCD (320x1480, capacitive touch)
Cameras: 2x Raspberry Pi Camera Module v3 (flush center-top, back-to-back)
GPS: u-blox NEO-6M breakout (38x26mm PCB with 25x25mm ceramic antenna)
Features: Magnetic dash mount, 9-degree wedge tilt, 30mm fan,
          4-piece snap-fit enclosure (prints on QIDI Q2 270x270x256mm)
Print material: PETG recommended (heat + vibration + UV resistant)

V2.1 changes from V2:
  - Cameras moved from protruding end housings to flush back-to-back center-top
  - End zones eliminated — bar trimmed to display width + bezel
  - Wedge angle reduced from 12 to 9 degrees (front wall 20mm for camera depth)
  - Bar taller than display to fit camera section above screen

Loadable by cadquery-server via show_object().
"""

import cadquery as cq
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Waveshare 11.9" DSI LCD ---
DISP_PCB_W = 287.3     # display PCB length
DISP_PCB_H = 69.8      # display PCB height (short axis)
DISP_PCB_T = 5.0       # PCB + touch glass total thickness
DISP_ACTIVE_W = 268.2  # active display area length
DISP_ACTIVE_H = 58.0   # active display area height
DSI_CABLE_GAP = 3.0    # gap behind display for DSI ribbon cable fold

# --- Raspberry Pi 5 (official mechanical drawing) ---
PI_W = 85.0            # board length (official: 85mm)
PI_D = 56.0            # board width  (official: 56mm)
PI_PCB_H = 1.6         # PCB thickness
PI_MOUNT_HOLE = 2.75   # M2.5 mounting holes (clearance)
PI_HOLES = [           # from bottom-left corner of PCB
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
CAM_MOUNT_HOLE = 2.0   # M2 camera mount screw diameter
CAM_HOLE_SPACING_W = 21    # horizontal hole center-to-center
CAM_HOLE_SPACING_H = 12.5  # vertical hole center-to-center
CAM_ANGLE = 15         # degrees downward tilt for road view

# --- Camera pocket (flush center-top, back-to-back) ---
# Two Camera Module v3s back-to-back: total depth ≈ 2*CAM_H + gap
CAM_POCKET_W = 30      # pocket width (X) — camera board + clearance
CAM_POCKET_H = 28      # pocket height (Z) — camera board + tilt clearance
CAM_POCKET_D = 25      # pocket depth (Y) — two modules back-to-back + gap
CAM_POCKET_GAP = 2     # gap between the two camera PCBs

# --- GPS Module (u-blox NEO-6M breakout) ---
GPS_W = 26             # board width
GPS_D = 38             # board length
GPS_H = 8.5            # board height including antenna
GPS_MOUNT_HOLE = 3.0   # M3
GPS_ANTENNA_SIZE = 25  # ceramic antenna patch (25x25mm)
GPS_WINDOW_THICKNESS = 0.8  # thinned wall for RF transparency

# --- 30mm Fan ---
FAN_SIZE = 30
FAN_H = 10             # ref only — fan depth for stack clearance calc
FAN_MOUNT_HOLE = 3.2   # M3
FAN_HOLE_SPACING = 24  # center-to-center

# --- Neodymium magnets ---
MAGNET_DIA = 10
MAGNET_H = 3
MAGNET_COUNT = 4

# --- Case construction ---
WALL = 2.5             # wall thickness
TOL = 0.4              # fit tolerance

# --- Enclosure width (along X axis) ---
# No end zones — bar is trimmed to display PCB + minimal bezel
BEZEL_MARGIN = 4       # extra bezel beyond display PCB on each side
TOTAL_W = DISP_PCB_W + BEZEL_MARGIN * 2  # ~295mm

# --- Enclosure depths (along Y axis, front to rear) ---
# Internal stack: display(5) + gap(3) + standoff(5) + Pi(1.6) +
#   stacking(16) + HAT(5.5) + airflow(5) + fan(10) = ~51
# With walls: ~56mm. Wedge means front is thinner.
INTERNAL_DEPTH = 46    # deepest internal dimension at base (reduced from V2)
EXT_DEPTH = INTERNAL_DEPTH + WALL * 2  # ~51mm at thickest (rear base)
FRONT_DEPTH = 20       # front edge thickness at top (fits camera module)

# --- Enclosure height (along Z axis) ---
# Display zone + camera zone above it
CAM_ZONE_H = 25        # height of camera section above display
DISP_ZONE_H = DISP_PCB_H + WALL * 2 + TOL * 2  # ~75mm display zone
EXT_HEIGHT = DISP_ZONE_H + CAM_ZONE_H  # ~100mm total height
SPLIT_Z = DISP_ZONE_H / 2  # top-bottom shell split (at display zone midpoint)

# --- Snap-fit tabs ---
SNAP_W = 12
SNAP_H = 3
SNAP_DEPTH = 1.5
SNAP_POSITIONS_X = [-40, 0, 40]  # along X edges of each half

# --- Center seam joining (left-right halves) ---
SEAM_TAB_W = 8         # tongue-and-groove tab width
SEAM_TAB_D = 4         # tongue depth into mating half
SEAM_TAB_POSITIONS = [-25, -10, 10, 25]  # Z positions along seam
SEAM_SCREW_HOLE = 3.2  # M3 through-hole
SEAM_BOSS_R = 5        # screw boss outer radius

# --- Standoff dimensions ---
STANDOFF_H = 5         # Pi mounting standoff height
STANDOFF_OUTER_R = 3   # standoff post outer radius

# --- Status indicators ---
LED_DIA = 3            # recording LED
STATUS_LED_W = 8       # Pi activity LED window width
STATUS_LED_H = 3       # Pi activity LED window height

# --- Port cutouts ---
USBC_W = 12            # USB-C port cutout width
USBC_H = 8             # USB-C port cutout height
SD_SLOT_W = 14         # microSD slot cutout width
SD_SLOT_H = 3          # microSD slot cutout height
PWR_BTN_DIA = 7        # power button access hole
CABLE_CHAN_W = 10       # cable routing channel width
CABLE_CHAN_H = 8        # cable routing channel height

# --- CSI ribbon cable ---
CSI_SLOT_W = 17        # CSI ribbon cable slot width
CSI_SLOT_H = 3         # CSI ribbon cable slot height

# --- Ventilation grid ---
VENT_SLOT_W = 2
VENT_SLOT_L = 5
VENT_GAP = 3.5

# --- Steel mounting plate (for reference / template) ---
PLATE_W = 250
PLATE_D = 40
PLATE_H = 1


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
# HELPER: Magnet recess
# =============================================================================

def build_magnet_recess(x, y):
    """Create a cylindrical recess for a neodymium disc magnet at position (x, y)."""
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(MAGNET_DIA / 2 + TOL)
        .extrude(MAGNET_H + 0.5)
    )


# =============================================================================
# HELPER: Flush camera pocket (center-top, back-to-back)
# =============================================================================

def build_camera_pocket():
    """
    Create a cuttable solid representing the camera pocket for two back-to-back
    Camera Module v3s. The pocket sits at the top-center of the bar.

    The pocket contains:
    - Main cavity for two camera modules back-to-back
    - Front lens aperture (flush with front wall)
    - Rear lens aperture (flush with rear wall)
    - M2 screw holes for each camera (4 per camera, 8 total)
    - CSI ribbon cable exit slot at the bottom of the pocket

    Built at origin, centered on X=0. The caller positions it at
    the correct Z height (top of the enclosure).
    """
    # Main pocket cavity — fits two modules back-to-back
    pocket = (
        cq.Workplane("XY")
        .box(CAM_POCKET_W + TOL * 2, CAM_POCKET_D + TOL * 2,
             CAM_POCKET_H + TOL * 2, centered=True)
    )

    # Front lens aperture — through the front wall (+Y face)
    # Lens is centered in the pocket, offset forward by half the pocket depth
    front_lens = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2 + 1)
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(-(WALL + 4))
    )
    pocket = pocket.union(front_lens)

    # Rear lens aperture — through the rear wall (-Y face)
    # At the top of the wedge, the rear wall Y position depends on the wedge.
    # We cut generously and let the shell boundary clip it.
    rear_lens = (
        cq.Workplane("XZ")
        .workplane(offset=-(EXT_DEPTH / 2 + 1))
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(WALL + 4)
    )
    pocket = pocket.union(rear_lens)

    # Front camera M2 screw holes (4 holes, camera faces +Y)
    for dx in [-CAM_HOLE_SPACING_W / 2, CAM_HOLE_SPACING_W / 2]:
        for dz in [-CAM_HOLE_SPACING_H / 2, CAM_HOLE_SPACING_H / 2]:
            hole = (
                cq.Workplane("XZ")
                .center(dx, dz)
                .workplane(offset=CAM_POCKET_D / 4)
                .circle(CAM_MOUNT_HOLE / 2)
                .extrude(CAM_POCKET_D / 2)
            )
            pocket = pocket.union(hole)

    # Rear camera M2 screw holes (4 holes, camera faces -Y)
    for dx in [-CAM_HOLE_SPACING_W / 2, CAM_HOLE_SPACING_W / 2]:
        for dz in [-CAM_HOLE_SPACING_H / 2, CAM_HOLE_SPACING_H / 2]:
            hole = (
                cq.Workplane("XZ")
                .center(dx, dz)
                .workplane(offset=-(CAM_POCKET_D / 4))
                .circle(CAM_MOUNT_HOLE / 2)
                .extrude(-(CAM_POCKET_D / 2))
            )
            pocket = pocket.union(hole)

    # CSI ribbon cable exit slot at the bottom of the pocket
    # Two slots side by side — one per camera cable
    for sx in [-8, 8]:
        csi_exit = (
            cq.Workplane("XY")
            .center(sx, 0)
            .workplane(offset=-(CAM_POCKET_H / 2 + 1))
            .box(CSI_SLOT_W, CSI_SLOT_H, 4, centered=True)
        )
        pocket = pocket.union(csi_exit)

    return pocket


# =============================================================================
# HELPER: Wedge shell and cavity
# =============================================================================

def build_wedge_shell(width):
    """
    Build a wedge-profiled outer shell for one half of the enclosure.

    The wedge cross-section (Y-Z plane) is a trapezoid:
    - Bottom edge: full EXT_DEPTH wide (flat on dashboard)
    - Top edge: FRONT_DEPTH wide (thin front bezel)
    - Height: EXT_HEIGHT
    - The front face (Y+) is vertical
    - The rear face (Y-) slopes forward as it rises

    Args:
        width: how wide this piece is along X
    """
    rear_top_y = EXT_DEPTH / 2 - FRONT_DEPTH

    wedge = (
        cq.Workplane("YZ")
        .moveTo(-EXT_DEPTH / 2, 0)           # bottom-rear
        .lineTo(EXT_DEPTH / 2, 0)            # bottom-front
        .lineTo(EXT_DEPTH / 2, EXT_HEIGHT)   # top-front
        .lineTo(rear_top_y, EXT_HEIGHT)      # top-rear (angled in)
        .close()
        .extrude(width)
    )

    wedge = wedge.translate((-(width / 2), 0, 0))
    return wedge


def build_wedge_cavity(width):
    """
    Build the internal cavity matching the wedge profile, offset by WALL
    on all sides. Used to hollow out the shell.
    """
    rear_top_y = EXT_DEPTH / 2 - FRONT_DEPTH + WALL

    cavity = (
        cq.Workplane("YZ")
        .moveTo(-(EXT_DEPTH / 2 - WALL), WALL)
        .lineTo(EXT_DEPTH / 2 - WALL, WALL)
        .lineTo(EXT_DEPTH / 2 - WALL, EXT_HEIGHT - WALL)
        .lineTo(rear_top_y, EXT_HEIGHT - WALL)
        .close()
        .extrude(width)
    )

    cavity = cavity.translate((-(width / 2), 0, 0))
    return cavity


# =============================================================================
# LEFT-BOTTOM (left base tray — no camera housing)
# =============================================================================

def build_left_bottom():
    """Left half of the bottom shell.
    Contains: magnet recesses, left-side Pi standoffs, vertical CSI cable
    channel, snap-fit ledge, center seam tongue tabs + screw boss.
    """
    half_w = TOTAL_W / 2  # ~148mm

    # --- Outer wedge shell (left half width) ---
    shell = build_wedge_shell(half_w)
    cavity = build_wedge_cavity(half_w)
    piece = shell.cut(cavity)

    # --- Cut at the split plane to keep only bottom half ---
    top_cutter = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z)
        .box(half_w + 10, EXT_DEPTH + 10, EXT_HEIGHT, centered=[True, True, False])
    )
    piece = piece.cut(top_cutter)

    # -------------------------------------------------------------------------
    # MAGNET RECESSES (2 magnets in left half, evenly spaced)
    # -------------------------------------------------------------------------
    magnet_spacing = PLATE_W / (MAGNET_COUNT + 1)
    for i in range(MAGNET_COUNT // 2):
        mx = -(half_w / 2) + magnet_spacing * (i + 1)
        recess = build_magnet_recess(mx, 0)
        piece = piece.cut(recess)

    # -------------------------------------------------------------------------
    # PI 5 MOUNTING STANDOFFS (left-side holes: indices 0 and 2)
    # Pi centered at X=0, Y shifted toward front (behind display)
    # -------------------------------------------------------------------------
    pi_center_y = EXT_DEPTH / 2 - WALL - DISP_PCB_T - DSI_CABLE_GAP - PI_D / 2

    for idx in [0, 2]:
        hx, hy = PI_HOLES[idx]
        px = hx - PI_W / 2
        py = pi_center_y + (hy - PI_D / 2)
        pz = WALL

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
        piece = piece.union(post)

    # -------------------------------------------------------------------------
    # CSI CABLE CHANNEL (vertical — from top of bottom half down to Pi)
    # Cameras are at top-center, cables route down through the side bezel
    # near the seam edge. Left half carries one cable channel.
    # -------------------------------------------------------------------------
    csi_channel = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(half_w / 2 - 10, pi_center_y + PI_D / 4)
        .box(CSI_SLOT_W, CSI_SLOT_H + 2, SPLIT_Z - WALL, centered=[True, True, False])
    )
    piece = piece.cut(csi_channel)

    # -------------------------------------------------------------------------
    # SNAP-FIT LEDGE (rim along top edge for top half to sit on)
    # -------------------------------------------------------------------------
    snap_ledge_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z - 2)
        .box(half_w - 2, EXT_DEPTH - 2, 2, centered=[True, True, False])
    )
    snap_ledge_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z - 2.5)
        .box(half_w - 6, EXT_DEPTH - 6, 3, centered=[True, True, False])
    )
    snap_ledge = snap_ledge_outer.cut(snap_ledge_inner)
    piece = piece.union(snap_ledge)

    # -------------------------------------------------------------------------
    # CENTER SEAM: tongue tabs (protrude from +X face)
    # -------------------------------------------------------------------------
    for tz in SEAM_TAB_POSITIONS:
        tab = (
            cq.Workplane("XY")
            .center(half_w / 2, 0)
            .workplane(offset=tz + SPLIT_Z / 2)
            .box(SEAM_TAB_D, SEAM_TAB_W, SEAM_TAB_W, centered=True)
        )
        piece = piece.union(tab)

    # Seam screw boss
    boss = (
        cq.Workplane("XY")
        .center(half_w / 2 - SEAM_BOSS_R, 0)
        .workplane(offset=SPLIT_Z / 2)
        .circle(SEAM_BOSS_R)
        .extrude(SPLIT_Z / 4)
    )
    boss_hole = (
        cq.Workplane("XY")
        .center(half_w / 2 - SEAM_BOSS_R, 0)
        .workplane(offset=SPLIT_Z / 2 - 1)
        .circle(SEAM_SCREW_HOLE / 2)
        .extrude(SPLIT_Z / 4 + 2)
    )
    boss = boss.cut(boss_hole)
    piece = piece.union(boss)

    return piece


# =============================================================================
# RIGHT-BOTTOM (right base tray — no camera housing)
# =============================================================================

def build_right_bottom():
    """Right half of the bottom shell.
    Contains: magnet recesses, right-side Pi standoffs, port cutouts
    (USB-C, microSD, power button), cable routing channel, recording LED,
    vertical CSI cable channel, snap-fit ledge, center seam groove slots.
    """
    half_w = TOTAL_W / 2

    # --- Outer wedge shell (right half) ---
    shell = build_wedge_shell(half_w)
    cavity = build_wedge_cavity(half_w)
    piece = shell.cut(cavity)

    # --- Keep only bottom half ---
    top_cutter = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z)
        .box(half_w + 10, EXT_DEPTH + 10, EXT_HEIGHT, centered=[True, True, False])
    )
    piece = piece.cut(top_cutter)

    # -------------------------------------------------------------------------
    # MAGNET RECESSES (2 magnets in right half)
    # -------------------------------------------------------------------------
    magnet_spacing = PLATE_W / (MAGNET_COUNT + 1)
    for i in range(MAGNET_COUNT // 2):
        mx = -(half_w / 2) + magnet_spacing * (i + 1)
        recess = build_magnet_recess(mx, 0)
        piece = piece.cut(recess)

    # -------------------------------------------------------------------------
    # PI 5 MOUNTING STANDOFFS (right-side holes: indices 1 and 3)
    # -------------------------------------------------------------------------
    pi_center_y = EXT_DEPTH / 2 - WALL - DISP_PCB_T - DSI_CABLE_GAP - PI_D / 2

    for idx in [1, 3]:
        hx, hy = PI_HOLES[idx]
        px = hx - PI_W / 2
        py = pi_center_y + (hy - PI_D / 2)
        pz = WALL

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
        piece = piece.union(post)

    # -------------------------------------------------------------------------
    # PORT CUTOUTS (right side wall)
    # -------------------------------------------------------------------------
    usbc_z = WALL + STANDOFF_H + PI_PCB_H + 1.6
    usbc = (
        cq.Workplane("YZ")
        .workplane(offset=half_w / 4)
        .center(pi_center_y - PI_D / 2 + 11.2, usbc_z)
        .rect(USBC_W, USBC_H)
        .extrude(WALL + 2)
    )
    piece = piece.cut(usbc)

    cable_chan = (
        cq.Workplane("YZ")
        .workplane(offset=half_w / 4)
        .center(pi_center_y - PI_D / 2 + 11.2, WALL + 2)
        .rect(CABLE_CHAN_W, CABLE_CHAN_H)
        .extrude(WALL + 2)
    )
    piece = piece.cut(cable_chan)

    sd_slot = (
        cq.Workplane("YZ")
        .workplane(offset=-(half_w / 4))
        .center(pi_center_y, WALL + 2)
        .rect(SD_SLOT_W, SD_SLOT_H)
        .extrude(-(WALL + 2))
    )
    piece = piece.cut(sd_slot)

    pwr_btn = (
        cq.Workplane("YZ")
        .workplane(offset=half_w / 4)
        .center(pi_center_y + PI_D / 2 - 5, WALL + STANDOFF_H + PI_PCB_H + 3)
        .circle(PWR_BTN_DIA / 2)
        .extrude(WALL + 2)
    )
    piece = piece.cut(pwr_btn)

    # -------------------------------------------------------------------------
    # RECORDING LED (front face)
    # -------------------------------------------------------------------------
    rec_led = (
        cq.Workplane("XZ")
        .center(10, SPLIT_Z / 3)
        .workplane(offset=EXT_DEPTH / 2)
        .circle(LED_DIA / 2)
        .extrude(WALL * 3)
    )
    piece = piece.cut(rec_led)

    # -------------------------------------------------------------------------
    # CSI CABLE CHANNEL (vertical — right half carries second cable)
    # -------------------------------------------------------------------------
    csi_channel = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(-(half_w / 2) + 10, pi_center_y + PI_D / 4)
        .box(CSI_SLOT_W, CSI_SLOT_H + 2, SPLIT_Z - WALL, centered=[True, True, False])
    )
    piece = piece.cut(csi_channel)

    # -------------------------------------------------------------------------
    # SNAP-FIT LEDGE
    # -------------------------------------------------------------------------
    snap_ledge_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z - 2)
        .box(half_w - 2, EXT_DEPTH - 2, 2, centered=[True, True, False])
    )
    snap_ledge_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z - 2.5)
        .box(half_w - 6, EXT_DEPTH - 6, 3, centered=[True, True, False])
    )
    snap_ledge = snap_ledge_outer.cut(snap_ledge_inner)
    piece = piece.union(snap_ledge)

    # -------------------------------------------------------------------------
    # CENTER SEAM: groove slots (receive tongues from left half)
    # -------------------------------------------------------------------------
    for tz in SEAM_TAB_POSITIONS:
        groove = (
            cq.Workplane("XY")
            .center(-(half_w / 2), 0)
            .workplane(offset=tz + SPLIT_Z / 2)
            .box(SEAM_TAB_D + TOL, SEAM_TAB_W + TOL, SEAM_TAB_W + TOL, centered=True)
        )
        piece = piece.cut(groove)

    boss = (
        cq.Workplane("XY")
        .center(-(half_w / 2) + SEAM_BOSS_R, 0)
        .workplane(offset=SPLIT_Z / 2)
        .circle(SEAM_BOSS_R)
        .extrude(SPLIT_Z / 4)
    )
    boss_hole = (
        cq.Workplane("XY")
        .center(-(half_w / 2) + SEAM_BOSS_R, 0)
        .workplane(offset=SPLIT_Z / 2 - 1)
        .circle(SEAM_SCREW_HOLE / 2)
        .extrude(SPLIT_Z / 4 + 2)
    )
    boss = boss.cut(boss_hole)
    piece = piece.union(boss)

    return piece


# =============================================================================
# LEFT-TOP (left display bezel + rear panel + GPS recess left portion)
# =============================================================================

def build_left_top():
    """Left half of the top shell.
    Contains: left display bezel, rear panel vents (left portion),
    left portion of GPS recess + antenna window, snap-fit tabs,
    center seam tongue tabs.
    """
    half_w = TOTAL_W / 2

    # --- Outer wedge shell ---
    shell = build_wedge_shell(half_w)
    cavity = build_wedge_cavity(half_w)
    piece = shell.cut(cavity)

    # --- Keep only top half (above SPLIT_Z) ---
    bottom_cutter = (
        cq.Workplane("XY")
        .box(half_w + 10, EXT_DEPTH + 10, SPLIT_Z, centered=[True, True, False])
    )
    piece = piece.cut(bottom_cutter)

    # -------------------------------------------------------------------------
    # DISPLAY BEZEL OPENING (front face, sized for the display active area)
    # The display panel sits in a lip/frame. The opening is slightly larger
    # than the active area to expose the full screen.
    # -------------------------------------------------------------------------
    # Display opening spans the full width of the piece but only the left half
    # of the active area. Opening is in the front face (Y = EXT_DEPTH/2).
    bezel_opening = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2 - WALL + 0.5)
        .center(0, EXT_HEIGHT / 2)
        .box(half_w - WALL * 2, DISP_ACTIVE_H + 2, WALL + 1, centered=True)
    )
    piece = piece.cut(bezel_opening)

    # Display panel lip (shelf for the display PCB to sit on, 2mm deep)
    disp_lip = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2 - WALL - 2)
        .center(0, EXT_HEIGHT / 2)
        .box(half_w - WALL, DISP_PCB_H + TOL * 2, 2, centered=True)
    )
    piece = piece.cut(disp_lip)

    # -------------------------------------------------------------------------
    # REAR PANEL VENTILATION (exhaust vents on rear face, left portion)
    # -------------------------------------------------------------------------
    vent_grid = make_vent_grid(4, 3, VENT_SLOT_W, VENT_SLOT_L, 4, VENT_GAP, WALL)
    # Position on rear face (-Y), centered vertically in top half
    rear_vents = vent_grid.translate((-(half_w / 4), -(EXT_DEPTH / 2), EXT_HEIGHT * 3 / 4))
    rear_vents = rear_vents.rotateAboutCenter((1, 0, 0), 90)
    piece = piece.cut(rear_vents)

    # -------------------------------------------------------------------------
    # GPS MODULE RECESS (top-rear surface, left portion)
    # GPS is centered at X=0 in full assembly, so it straddles the seam.
    # Left half gets the left portion of the recess.
    # -------------------------------------------------------------------------
    # GPS recess (full size, positioned at X=0, then only the left portion
    # remains after the piece boundary clips it)
    gps_recess = (
        cq.Workplane("XY")
        .center(half_w / 2 - 5, -(EXT_DEPTH / 4))
        .workplane(offset=EXT_HEIGHT - WALL - GPS_H / 2)
        .box(GPS_W + TOL * 2, GPS_D + TOL * 2, GPS_H + 1, centered=True)
    )
    piece = piece.cut(gps_recess)

    # Thinned antenna window
    gps_window = (
        cq.Workplane("XY")
        .center(half_w / 2 - 5, -(EXT_DEPTH / 4))
        .workplane(offset=EXT_HEIGHT - GPS_WINDOW_THICKNESS)
        .box(GPS_ANTENNA_SIZE - 4, GPS_ANTENNA_SIZE - 4, WALL, centered=True)
    )
    piece = piece.cut(gps_window)

    # GPS M3 mount holes (left-side pair only)
    for gy in [-(GPS_D / 2 - 2), (GPS_D / 2 - 2)]:
        gps_hole = (
            cq.Workplane("XY")
            .center(half_w / 2 - 5 - (GPS_W / 2 - 2), -(EXT_DEPTH / 4) + gy)
            .workplane(offset=EXT_HEIGHT - WALL - GPS_H)
            .circle(GPS_MOUNT_HOLE / 2)
            .extrude(GPS_H + WALL + 2)
        )
        piece = piece.cut(gps_hole)

    # -------------------------------------------------------------------------
    # SNAP-FIT INNER RIM + TABS (mates with bottom half's ledge)
    # -------------------------------------------------------------------------
    snap_rim_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z + 1)
        .box(half_w - 2, EXT_DEPTH - 2, 2.5, centered=True)
    )
    snap_rim_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z + 1)
        .box(half_w - 5, EXT_DEPTH - 5, 3.5, centered=True)
    )
    snap_rim = snap_rim_outer.cut(snap_rim_inner)
    piece = piece.union(snap_rim)

    # Snap-fit tabs along long edges (front + rear)
    for zpos in SNAP_POSITIONS_Z:
        for y_sign in [1, -1]:  # front and rear edges
            tab = (
                cq.Workplane("XY")
                .center(zpos, y_sign * (EXT_DEPTH / 2 - WALL))
                .workplane(offset=SPLIT_Z + 1)
                .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
            )
            piece = piece.union(tab)

    # -------------------------------------------------------------------------
    # CENTER SEAM: tongue tabs (+X face)
    # -------------------------------------------------------------------------
    for tz in SEAM_TAB_POSITIONS:
        tab = (
            cq.Workplane("XY")
            .center(half_w / 2, 0)
            .workplane(offset=tz + EXT_HEIGHT * 3 / 4)
            .box(SEAM_TAB_D, SEAM_TAB_W, SEAM_TAB_W, centered=True)
        )
        piece = piece.union(tab)

    return piece


# =============================================================================
# RIGHT-TOP (right display bezel + fan mount + GPS recess right portion)
# =============================================================================

def build_right_top():
    """Right half of the top shell.
    Contains: right display bezel, 30mm fan mount with screw holes,
    right portion of GPS recess, Pi activity LED window, rear panel vents,
    snap-fit tabs, center seam groove slots.
    """
    half_w = TOTAL_W / 2

    # --- Outer wedge shell ---
    shell = build_wedge_shell(half_w)
    cavity = build_wedge_cavity(half_w)
    piece = shell.cut(cavity)

    # --- Keep only top half ---
    bottom_cutter = (
        cq.Workplane("XY")
        .box(half_w + 10, EXT_DEPTH + 10, SPLIT_Z, centered=[True, True, False])
    )
    piece = piece.cut(bottom_cutter)

    # -------------------------------------------------------------------------
    # DISPLAY BEZEL OPENING (right half of active area)
    # -------------------------------------------------------------------------
    bezel_opening = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2 - WALL + 0.5)
        .center(0, EXT_HEIGHT / 2)
        .box(half_w - WALL * 2, DISP_ACTIVE_H + 2, WALL + 1, centered=True)
    )
    piece = piece.cut(bezel_opening)

    disp_lip = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2 - WALL - 2)
        .center(0, EXT_HEIGHT / 2)
        .box(half_w - WALL, DISP_PCB_H + TOL * 2, 2, centered=True)
    )
    piece = piece.cut(disp_lip)

    # -------------------------------------------------------------------------
    # 30mm FAN MOUNT (rear wall, centered over AI HAT position)
    # Fan is in the right half since the Pi center is at X=0 and the fan
    # sits directly above the HAT. Position near the seam edge.
    # -------------------------------------------------------------------------

    # Fan center position: near seam (X ≈ -half_w/2 + some offset),
    # on the rear wall, vertically centered in the top half
    fan_cx = -(half_w / 4)  # slightly left of center in right half
    fan_cy = -(EXT_DEPTH / 2)  # rear face
    fan_cz = EXT_HEIGHT * 3 / 4  # vertically centered in top half

    # Fan intake hole through rear wall
    fan_hole = (
        cq.Workplane("XZ")
        .center(fan_cx, fan_cz)
        .workplane(offset=fan_cy)
        .circle(FAN_SIZE / 2 - 2)
        .extrude(-(WALL + 2))
    )
    piece = piece.cut(fan_hole)

    # Fan M3 screw holes (4 corners)
    for fx in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
        for fz in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
            fan_screw = (
                cq.Workplane("XZ")
                .center(fan_cx + fx, fan_cz + fz)
                .workplane(offset=fan_cy)
                .circle(FAN_MOUNT_HOLE / 2)
                .extrude(-(WALL + 2))
            )
            piece = piece.cut(fan_screw)

    # Fan intake ventilation grid around the fan opening
    fan_vent_grid = make_vent_grid(3, 3, 2, 3, 4, 4, WALL)
    fan_vents = fan_vent_grid.translate((fan_cx, fan_cy, fan_cz))
    fan_vents = fan_vents.rotateAboutCenter((1, 0, 0), 90)
    piece = piece.cut(fan_vents)

    # -------------------------------------------------------------------------
    # REAR PANEL VENTILATION (right portion)
    # -------------------------------------------------------------------------
    vent_grid_rear = make_vent_grid(4, 3, VENT_SLOT_W, VENT_SLOT_L, 4, VENT_GAP, WALL)
    rear_vents = vent_grid_rear.translate((half_w / 4, -(EXT_DEPTH / 2), EXT_HEIGHT * 3 / 4))
    rear_vents = rear_vents.rotateAboutCenter((1, 0, 0), 90)
    piece = piece.cut(rear_vents)

    # -------------------------------------------------------------------------
    # GPS MODULE RECESS (right portion — straddles seam)
    # -------------------------------------------------------------------------
    gps_recess = (
        cq.Workplane("XY")
        .center(-(half_w / 2) + 5, -(EXT_DEPTH / 4))
        .workplane(offset=EXT_HEIGHT - WALL - GPS_H / 2)
        .box(GPS_W + TOL * 2, GPS_D + TOL * 2, GPS_H + 1, centered=True)
    )
    piece = piece.cut(gps_recess)

    # GPS antenna window (right portion)
    gps_window = (
        cq.Workplane("XY")
        .center(-(half_w / 2) + 5, -(EXT_DEPTH / 4))
        .workplane(offset=EXT_HEIGHT - GPS_WINDOW_THICKNESS)
        .box(GPS_ANTENNA_SIZE - 4, GPS_ANTENNA_SIZE - 4, WALL, centered=True)
    )
    piece = piece.cut(gps_window)

    # GPS M3 mount holes (right-side pair)
    for gy in [-(GPS_D / 2 - 2), (GPS_D / 2 - 2)]:
        gps_hole = (
            cq.Workplane("XY")
            .center(-(half_w / 2) + 5 + (GPS_W / 2 - 2), -(EXT_DEPTH / 4) + gy)
            .workplane(offset=EXT_HEIGHT - WALL - GPS_H)
            .circle(GPS_MOUNT_HOLE / 2)
            .extrude(GPS_H + WALL + 2)
        )
        piece = piece.cut(gps_hole)

    # -------------------------------------------------------------------------
    # PI ACTIVITY LED WINDOW (optional, on front face near bottom-right)
    # -------------------------------------------------------------------------
    status_led = (
        cq.Workplane("XZ")
        .workplane(offset=EXT_DEPTH / 2)
        .center(half_w / 4, SPLIT_Z + 5)
        .rect(STATUS_LED_W, STATUS_LED_H)
        .extrude(WALL * 3)
    )
    piece = piece.cut(status_led)

    # -------------------------------------------------------------------------
    # SNAP-FIT INNER RIM + TABS
    # -------------------------------------------------------------------------
    snap_rim_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z + 1)
        .box(half_w - 2, EXT_DEPTH - 2, 2.5, centered=True)
    )
    snap_rim_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_Z + 1)
        .box(half_w - 5, EXT_DEPTH - 5, 3.5, centered=True)
    )
    snap_rim = snap_rim_outer.cut(snap_rim_inner)
    piece = piece.union(snap_rim)

    for zpos in SNAP_POSITIONS_Z:
        for y_sign in [1, -1]:
            tab = (
                cq.Workplane("XY")
                .center(zpos, y_sign * (EXT_DEPTH / 2 - WALL))
                .workplane(offset=SPLIT_Z + 1)
                .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
            )
            piece = piece.union(tab)

    # -------------------------------------------------------------------------
    # CENTER SEAM: groove slots (-X face, receives tongues from left-top)
    # -------------------------------------------------------------------------
    for tz in SEAM_TAB_POSITIONS:
        groove = (
            cq.Workplane("XY")
            .center(-(half_w / 2), 0)
            .workplane(offset=tz + EXT_HEIGHT * 3 / 4)
            .box(SEAM_TAB_D + TOL, SEAM_TAB_W + TOL, SEAM_TAB_W + TOL, centered=True)
        )
        piece = piece.cut(groove)

    return piece


# =============================================================================
# STEEL MOUNTING PLATE (template for laser cutting / reference)
# =============================================================================

def build_mounting_plate():
    """Flat steel plate outline for magnetic dash mount.
    Print this as a template or use for laser-cut ordering."""
    plate = (
        cq.Workplane("XY")
        .box(PLATE_W, PLATE_D, PLATE_H, centered=True)
    )
    plate = plate.edges("|Z").fillet(2)
    return plate


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

# Build all pieces
left_bottom = build_left_bottom()
right_bottom = build_right_bottom()
left_top = build_left_top()
right_top = build_right_top()
mount_plate = build_mounting_plate()

# --- Exploded assembly preview ---
# Bottom halves sit at Z=0, offset left/right from center
# Top halves float above with a 5mm exploded gap
EXPLODE_GAP = 5  # gap between top and bottom for visibility
SEAM_GAP = 1     # tiny gap at center seam for visibility

show_object(
    left_bottom.translate((-(TOTAL_W / 4 + SEAM_GAP / 2), 0, 0)),
    name="left_bottom",
    options={"color": (0.12, 0.12, 0.14, 0.9)},
)
show_object(
    right_bottom.translate((TOTAL_W / 4 + SEAM_GAP / 2, 0, 0)),
    name="right_bottom",
    options={"color": (0.15, 0.15, 0.17, 0.9)},
)
show_object(
    left_top.translate((-(TOTAL_W / 4 + SEAM_GAP / 2), 0, EXPLODE_GAP)),
    name="left_top",
    options={"color": (0.20, 0.20, 0.22, 0.85)},
)
show_object(
    right_top.translate((TOTAL_W / 4 + SEAM_GAP / 2, 0, EXPLODE_GAP)),
    name="right_top",
    options={"color": (0.23, 0.23, 0.25, 0.85)},
)

# Mounting plate below for reference
show_object(
    mount_plate.translate((0, 0, -15)),
    name="mounting_plate",
    options={"color": (0.55, 0.55, 0.60, 0.7)},
)
