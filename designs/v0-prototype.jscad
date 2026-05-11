// =============================================================================
// Pi 5 + AI HAT Dashcam Enclosure
// Dual Camera (Front + Rear) — Car Mount Design
// =============================================================================
// Designed for: Raspberry Pi 5 + AI HAT+ (Hailo-8L)
// Cameras: 2x Raspberry Pi Camera Module v3
// Purpose: In-car dashcam with AI-powered detection
// =============================================================================

const { union, subtract, intersection } = require('@jscad/modeling').booleans;
const { cube, cuboid, cylinder, roundedCuboid } = require('@jscad/modeling').primitives;
const { translate, rotate, mirror } = require('@jscad/modeling').transforms;
const { colorize } = require('@jscad/modeling').colors;

// -----------------------------------------------------------------------------
// DIMENSIONS (all in mm)
// -----------------------------------------------------------------------------

// Raspberry Pi 5
const PI_W = 85.6;       // length
const PI_D = 56.5;       // width
const PI_H = 1.6;        // PCB thickness
const PI_MOUNT_HOLE = 2.7; // M2.5 mounting holes

// Mounting hole positions (from bottom-left corner of Pi)
const PI_HOLES = [
  [3.5, 3.5],
  [3.5 + 58, 3.5],
  [3.5, 3.5 + 49],
  [3.5 + 58, 3.5 + 49]
];

// AI HAT+
const HAT_W = 65;
const HAT_D = 56.5;
const HAT_H = 5.5;
const STACKING_HEADER_H = 16; // height of stacking header

// Camera Module v3
const CAM_W = 25;
const CAM_D = 24;
const CAM_H = 11.5;
const LENS_DIA = 8;
const LENS_PROTRUSION = 5;

// Case parameters
const WALL = 2.0;          // wall thickness
const CORNER_R = 3;        // corner radius
const TOLERANCE = 0.5;     // fit tolerance
const VENT_SLOT_W = 2;     // ventilation slot width
const VENT_SLOT_GAP = 3;   // gap between vent slots

// Internal cavity
const INTERNAL_W = PI_W + TOLERANCE * 2;
const INTERNAL_D = PI_D + TOLERANCE * 2;
// Stack: standoffs(5) + Pi(1.6) + components(15) + stacking header(16) + HAT(5.5) + clearance(3)
const INTERNAL_H = 48;

// External dimensions
const EXT_W = INTERNAL_W + WALL * 2;
const EXT_D = INTERNAL_D + WALL * 2;
const EXT_H = INTERNAL_H + WALL * 2;

// Camera mount arm dimensions
const CAM_ARM_L = 20;      // length of camera arm
const CAM_ARM_W = 30;      // width of camera arm
const CAM_ARM_H = 16;      // height (enough for camera module)

// Windshield mount tab
const MOUNT_W = 40;
const MOUNT_D = 30;
const MOUNT_H = 4;
const MOUNT_HOLE_DIA = 6;  // for suction cup / adhesive mount bolt

// -----------------------------------------------------------------------------
// HELPER FUNCTIONS
// -----------------------------------------------------------------------------

function roundedBox(w, d, h, r) {
  return roundedCuboid({
    size: [w, d, h],
    roundRadius: r,
    segments: 16
  });
}

function mountingPost(x, y, height, innerDia, outerDia) {
  return translate([x, y, 0],
    subtract(
      cylinder({ radius: outerDia / 2, height: height, segments: 16 }),
      cylinder({ radius: innerDia / 2, height: height + 1, segments: 16 })
    )
  );
}

function ventSlots(count, slotW, slotH, gap, totalDepth) {
  const slots = [];
  const startX = -(count * (slotW + gap) - gap) / 2;
  for (let i = 0; i < count; i++) {
    slots.push(
      translate([startX + i * (slotW + gap), 0, 0],
        cuboid({ size: [slotW, totalDepth + 2, slotH] })
      )
    );
  }
  return union(...slots);
}

// -----------------------------------------------------------------------------
// MAIN CASE — BOTTOM HALF
// -----------------------------------------------------------------------------

function caseBottom() {
  // Outer shell
  const outer = roundedBox(EXT_W, EXT_D, EXT_H / 2, CORNER_R);

  // Inner cavity (shifted up by wall thickness)
  const inner = translate([0, 0, WALL],
    roundedBox(INTERNAL_W, INTERNAL_D, EXT_H / 2, CORNER_R - WALL / 2)
  );

  // USB-C power port cutout (bottom edge)
  const usbC = translate([-(EXT_W / 2), -(EXT_D / 4), WALL + 3],
    cuboid({ size: [WALL * 3, 12, 7] })
  );

  // USB 3.0 ports cutout (right side)
  const usb3 = translate([EXT_W / 4, EXT_D / 2, WALL + 5],
    cuboid({ size: [32, WALL * 3, 16] })
  );

  // Ethernet cutout (left side, optional — might not need for dashcam)
  const ethernet = translate([-(EXT_W / 4), EXT_D / 2, WALL + 3],
    cuboid({ size: [16, WALL * 3, 14] })
  );

  // Side ventilation
  const sideVents = translate([0, EXT_D / 2, EXT_H / 4],
    ventSlots(8, VENT_SLOT_W, 15, VENT_SLOT_GAP, WALL)
  );

  // Top ventilation (for AI HAT heat)
  const topVents = translate([0, 0, EXT_H / 2 - 0.5],
    rotate([0, 0, Math.PI / 2],
      ventSlots(10, VENT_SLOT_W, 30, VENT_SLOT_GAP, WALL)
    )
  );

  // CSI ribbon cable slots (two cameras)
  // Front camera ribbon exit
  const csiSlotFront = translate([EXT_W / 2, -8, WALL + 2],
    cuboid({ size: [WALL * 3, 17, 3] })
  );

  // Rear camera ribbon exit
  const csiSlotRear = translate([-(EXT_W / 2), -8, WALL + 2],
    cuboid({ size: [WALL * 3, 17, 3] })
  );

  // Mounting posts for Pi
  const posts = PI_HOLES.map(([x, y]) =>
    translate([x - INTERNAL_W / 2 + TOLERANCE, y - INTERNAL_D / 2 + TOLERANCE, -(EXT_H / 4) + WALL],
      mountingPost(0, 0, 5, PI_MOUNT_HOLE / 2, 5)
    )
  );

  // Screw holes for case closure (4 corners)
  const caseScrews = [
    [EXT_W / 2 - 5, EXT_D / 2 - 5],
    [-(EXT_W / 2 - 5), EXT_D / 2 - 5],
    [EXT_W / 2 - 5, -(EXT_D / 2 - 5)],
    [-(EXT_W / 2 - 5), -(EXT_D / 2 - 5)]
  ].map(([x, y]) =>
    translate([x, y, 0],
      cylinder({ radius: 1.5, height: EXT_H, segments: 16 })
    )
  );

  let bottom = subtract(outer, inner);
  bottom = subtract(bottom, usbC, usb3, csiSlotFront, csiSlotRear);
  bottom = subtract(bottom, sideVents, topVents);
  bottom = subtract(bottom, ...caseScrews);
  bottom = union(bottom, ...posts);

  // Shift so bottom sits on build plate
  return translate([0, 0, EXT_H / 4],
    colorize([0.2, 0.2, 0.2, 1], bottom)
  );
}

// -----------------------------------------------------------------------------
// CAMERA MOUNT ARM (x2 — front and rear)
// -----------------------------------------------------------------------------

function cameraMount(side) {
  // Camera housing
  const housing = roundedBox(CAM_ARM_W, CAM_ARM_H, CAM_W + WALL * 2, 2);

  // Camera cavity
  const cavity = cuboid({
    size: [CAM_D + TOLERANCE, CAM_H + TOLERANCE, CAM_W + TOLERANCE]
  });

  // Lens hole
  const lensHole = translate([0, CAM_ARM_H / 2, 0],
    rotate([Math.PI / 2, 0, 0],
      cylinder({ radius: LENS_DIA / 2 + 1, height: WALL * 3, segments: 24 })
    )
  );

  // Ribbon cable slot
  const ribbonSlot = translate([0, -(CAM_ARM_H / 2), 0],
    cuboid({ size: [17, WALL * 3, 3] })
  );

  let mount = subtract(housing, cavity, lensHole, ribbonSlot);

  // Connection arm to main case
  const arm = translate([0, 0, -(CAM_W / 2 + CAM_ARM_L / 2 + WALL)],
    cuboid({ size: [CAM_ARM_W, CAM_ARM_H, CAM_ARM_L] })
  );

  // Hinge hole for angle adjustment
  const hingeHole = translate([0, 0, -(CAM_W / 2 + CAM_ARM_L + WALL)],
    rotate([0, Math.PI / 2, 0],
      cylinder({ radius: 2.5, height: CAM_ARM_W + 2, segments: 16 })
    )
  );

  mount = union(mount, arm);
  mount = subtract(mount, hingeHole);

  // Position: front camera points forward, rear camera points backward
  const xOffset = side === 'front' ? EXT_W / 2 + CAM_ARM_L : -(EXT_W / 2 + CAM_ARM_L);
  const angle = side === 'front' ? 0 : Math.PI;

  return translate([xOffset, 0, EXT_H / 2],
    rotate([0, 0, angle],
      colorize([0.3, 0.3, 0.3, 1], mount)
    )
  );
}

// -----------------------------------------------------------------------------
// WINDSHIELD MOUNT TAB
// -----------------------------------------------------------------------------

function windshieldMount() {
  const tab = roundedBox(MOUNT_W, MOUNT_D, MOUNT_H, 2);

  // Mount holes (for adhesive pad or suction cup)
  const hole1 = translate([10, 0, 0],
    cylinder({ radius: MOUNT_HOLE_DIA / 2, height: MOUNT_H + 2, segments: 16 })
  );
  const hole2 = translate([-10, 0, 0],
    cylinder({ radius: MOUNT_HOLE_DIA / 2, height: MOUNT_H + 2, segments: 16 })
  );

  // Slot for zip tie / strap
  const slot = cuboid({ size: [25, 3, MOUNT_H + 2] });

  const mount = subtract(tab, hole1, hole2, slot);

  return translate([0, 0, EXT_H / 2 + MOUNT_H / 2 + WALL],
    colorize([0.15, 0.15, 0.15, 1], mount)
  );
}

// -----------------------------------------------------------------------------
// ASSEMBLY
// -----------------------------------------------------------------------------

function main() {
  return [
    caseBottom(),
    cameraMount('front'),
    cameraMount('rear'),
    windshieldMount()
  ];
}

module.exports = { main };
