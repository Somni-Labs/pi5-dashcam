"""
Pi 5 + AI HAT Dashcam Enclosure -- V0 Prototype
Simplified version for quick test printing.

Just the basics: box enclosure, Pi mounting posts, camera lens holes,
USB-C port, and microSD slot. No GPS, no fan mount, no snap-fit,
no ventilation grids. Single-piece open-top tray.

Print material: PLA fine for prototyping fit checks.
Loadable by cadquery-server via show_object().
"""

import cadquery as cq
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Raspberry Pi 5 ---
PI_W = 85.6
PI_D = 56.5
PI_MOUNT_HOLE = 2.7    # M2.5

# Mounting hole positions (from bottom-left corner)
PI_HOLES = [
    (3.5, 3.5),
    (61.5, 3.5),
    (3.5, 52.5),
    (61.5, 52.5),
]

# --- Case construction ---
WALL = 2.0             # thinner wall OK for prototype
TOL = 0.5              # looser tolerance for test fit
CORNER_R = 3

# Internal stack: standoffs(5) + Pi(1.6) + components(15) + header(16) + HAT(5.5) + clearance(3)
INTERNAL_H = 48

INT_W = PI_W + TOL * 2
INT_D = PI_D + TOL * 2

EXT_W = INT_W + WALL * 2
EXT_D = INT_D + WALL * 2
EXT_H = INTERNAL_H + WALL * 2

# --- Camera ---
LENS_DIA = 8

# --- Standoffs ---
STANDOFF_H = 5
STANDOFF_OUTER_R = 2.5

# --- Ports ---
USBC_W = 12
USBC_H = 7
SD_SLOT_W = 14
SD_SLOT_H = 3


# =============================================================================
# BUILD PROTOTYPE TRAY (open-top single piece)
# =============================================================================

def build_prototype():
    """
    Simple open-top tray with Pi mounting posts and basic cutouts.
    No lid, no snap-fit -- just enough to verify Pi fit and camera alignment.
    """

    # Outer box
    tray = (
        cq.Workplane("XY")
        .box(EXT_W, EXT_D, EXT_H, centered=[True, True, False])
    )
    tray = tray.edges("|Z").fillet(CORNER_R)

    # Hollow out interior (open top)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .box(INT_W, INT_D, EXT_H, centered=[True, True, False])
    )
    tray = tray.cut(cavity)

    # -------------------------------------------------------------------------
    # Pi 5 MOUNTING POSTS (5mm standoffs from floor)
    # -------------------------------------------------------------------------

    for hx, hy in PI_HOLES:
        px = hx - INT_W / 2 + TOL
        py = hy - INT_D / 2 + TOL

        standoff = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=WALL)
            .circle(STANDOFF_OUTER_R)
            .extrude(STANDOFF_H)
        )
        screw_hole = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=WALL - 0.5)
            .circle(PI_MOUNT_HOLE / 2)
            .extrude(STANDOFF_H + 1)
        )
        post = standoff.cut(screw_hole)
        tray = tray.union(post)

    # -------------------------------------------------------------------------
    # CAMERA LENS HOLES (front and rear walls, simple circles)
    # -------------------------------------------------------------------------

    # Front camera lens hole (centered on front wall)
    front_lens = (
        cq.Workplane("XZ")
        .center(0, EXT_H / 2)
        .workplane(offset=EXT_D / 2)
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(WALL * 2)
    )
    tray = tray.cut(front_lens)

    # Rear camera lens hole (centered on rear wall)
    rear_lens = (
        cq.Workplane("XZ")
        .center(0, EXT_H / 2)
        .workplane(offset=-(EXT_D / 2))
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(-(WALL * 2))
    )
    tray = tray.cut(rear_lens)

    # -------------------------------------------------------------------------
    # USB-C PORT CUTOUT (left side wall)
    # -------------------------------------------------------------------------

    usbc = (
        cq.Workplane("XY")
        .center(-(EXT_W / 2), 15)
        .workplane(offset=WALL + 4)
        .box(WALL * 3, USBC_W, USBC_H, centered=True)
    )
    tray = tray.cut(usbc)

    # -------------------------------------------------------------------------
    # microSD SLOT (right side wall)
    # -------------------------------------------------------------------------

    sd_slot = (
        cq.Workplane("XY")
        .center(EXT_W / 2, -20)
        .workplane(offset=WALL + 2)
        .box(WALL * 3, SD_SLOT_W, SD_SLOT_H, centered=True)
    )
    tray = tray.cut(sd_slot)

    # -------------------------------------------------------------------------
    # CSI RIBBON CABLE SLOTS (front and rear walls, simple rectangular slots)
    # -------------------------------------------------------------------------

    # Front CSI slot
    csi_front = (
        cq.Workplane("XY")
        .center(12, EXT_D / 2)
        .workplane(offset=WALL + 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    tray = tray.cut(csi_front)

    # Rear CSI slot
    csi_rear = (
        cq.Workplane("XY")
        .center(-12, -(EXT_D / 2))
        .workplane(offset=WALL + 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    tray = tray.cut(csi_rear)

    return tray


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

prototype = build_prototype()

show_object(prototype, name="prototype_tray", options={"color": (0.3, 0.3, 0.3, 0.9)})
