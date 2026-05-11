// =============================================================================
// Pi 5 + AI HAT Dashcam Enclosure — V1
// Dual Camera (Front + Rear) — Car Mount Design
// =============================================================================
// Designed for: Raspberry Pi 5 + AI HAT+ (Hailo-8L)
// Cameras: 2x Raspberry Pi Camera Module v3 (integrated mounts)
// GPS: u-blox NEO-6M/7M/8M module (25x25mm standard)
// Features: Snap-fit closure, 30mm fan, status LED, power button access
// Print material: PETG recommended (heat + vibration resistant)
// =============================================================================

const { union, subtract } = require('@jscad/modeling').booleans;
const { cuboid, cylinder, roundedCuboid } = require('@jscad/modeling').primitives;
const { translate, rotate } = require('@jscad/modeling').transforms;
const { colorize } = require('@jscad/modeling').colors;

// -----------------------------------------------------------------------------
// DIMENSIONS (all in mm)
// -----------------------------------------------------------------------------

// Raspberry Pi 5
const PI_W = 85.6;
const PI_D = 56.5;
const PI_PCB_H = 1.6;
const PI_MOUNT_HOLE = 2.7;       // M2.5

// Pi 5 mounting holes (from bottom-left corner)
const PI_HOLES = [
  [3.5, 3.5],
  [61.5, 3.5],
  [3.5, 52.5],
  [61.5, 52.5]
];

// AI HAT+
const HAT_H = 5.5;
const STACKING_H = 16;

// Camera Module v3
const CAM_W = 25;
const CAM_D = 24;
const CAM_H = 11.5;
const LENS_DIA = 8;
const LENS_PROTRUSION = 5;
const CAM_MOUNT_HOLE = 2.0;      // M2
const CAM_HOLE_SPACING_W = 21;   // horizontal hole spacing
const CAM_HOLE_SPACING_H = 12.5; // vertical hole spacing

// GPS Module (u-blox NEO standard)
const GPS_W = 25;
const GPS_D = 25;
const GPS_H = 4;
const GPS_MOUNT_HOLE = 3.0;      // M3

// 30mm Fan
const FAN_SIZE = 30;
const FAN_H = 10;
const FAN_MOUNT_HOLE = 3.2;      // M3
const FAN_HOLE_SPACING = 24;     // center-to-center

// Case parameters
const WALL = 2.5;                 // thicker for car vibration
const CORNER_R = 3;
const TOL = 0.4;                  // fit tolerance

// Internal stack height:
// standoffs(5) + Pi PCB(1.6) + under-board components(3.5) +
// active cooler(15) + stacking header(16) + HAT(5.5) + clearance(3)
const INTERNAL_H = 50;

// Internal cavity
const INT_W = PI_W + TOL * 2;
const INT_D = PI_D + TOL * 2;

// Camera integration adds depth to front/rear walls
const CAM_POCKET_DEPTH = CAM_H + LENS_PROTRUSION + 2;
const CAM_ANGLE = 15;             // degrees downward tilt

// External dimensions
const EXT_W = INT_W + WALL * 2;
const EXT_D = INT_D + WALL * 2 + CAM_POCKET_DEPTH * 2; // extra for camera pockets
const EXT_H = INTERNAL_H + WALL * 2;
const SPLIT_H = EXT_H / 2;       // case splits in half

// Snap-fit tab dimensions
const SNAP_W = 12;
const SNAP_H = 3;
const SNAP_DEPTH = 1.5;
const SNAP_POSITIONS = [-30, -10, 10, 30]; // x positions for snap tabs

// Windshield mount
const MOUNT_W = 50;
const MOUNT_D = 35;
const MOUNT_H = 4;
const MOUNT_SLOT_W = 30;
const MOUNT_SLOT_D = 4;

// Recording LED
const LED_DIA = 3;

// Power button
const PWR_BTN_DIA = 7;

// Status LED window
const STATUS_LED_W = 8;
const STATUS_LED_H = 3;

// Cable routing channel
const CABLE_CHAN_W = 10;
const CABLE_CHAN_H = 8;

// microSD slot
const SD_SLOT_W = 14;
const SD_SLOT_H = 3;

// -----------------------------------------------------------------------------
// HELPERS
// -----------------------------------------------------------------------------

function rbox(w, d, h, r) {
  return roundedCuboid({ size: [w, d, h], roundRadius: Math.min(r, w/2, d/2, h/2), segments: 16 });
}

function cyl(r, h, segs) {
  return cylinder({ radius: r, height: h, segments: segs || 24 });
}

function post(x, y, h, innerR, outerR) {
  return translate([x, y, 0],
    subtract(
      cyl(outerR, h),
      cyl(innerR, h + 1)
    )
  );
}

function ventGrid(countX, countY, slotW, slotL, gapX, gapY, depth) {
  const slots = [];
  const startX = -(countX * (slotW + gapX) - gapX) / 2;
  const startY = -(countY * (slotL + gapY) - gapY) / 2;
  for (let i = 0; i < countX; i++) {
    for (let j = 0; j < countY; j++) {
      slots.push(
        translate([startX + i * (slotW + gapX), startY + j * (slotL + gapY), 0],
          cuboid({ size: [slotW, slotL, depth + 2] })
        )
      );
    }
  }
  return union(...slots);
}

// -----------------------------------------------------------------------------
// BOTTOM HALF
// -----------------------------------------------------------------------------

function bottomHalf() {
  // Outer shell — bottom half
  let outer = rbox(EXT_W, EXT_D, SPLIT_H, CORNER_R);

  // Inner cavity
  const inner = translate([0, 0, WALL],
    cuboid({ size: [INT_W, INT_D, SPLIT_H] })
  );

  // Camera pocket — FRONT (positive Y wall)
  // Angled pocket integrated into front wall
  const frontCamPocket = translate([0, INT_D / 2 + WALL + CAM_POCKET_DEPTH / 2 - 1, 2],
    rotate([Math.PI * CAM_ANGLE / 180, 0, 0],
      cuboid({ size: [CAM_W + TOL * 2, CAM_POCKET_DEPTH, CAM_D + TOL * 2] })
    )
  );

  // Front lens hole
  const frontLens = translate([0, EXT_D / 2, 2],
    rotate([Math.PI / 2 + Math.PI * CAM_ANGLE / 180, 0, 0],
      cyl(LENS_DIA / 2 + 1.5, WALL * 4)
    )
  );

  // Front camera mount screw holes (M2)
  const frontCamHoles = [
    [-CAM_HOLE_SPACING_W / 2, 0, -CAM_HOLE_SPACING_H / 2],
    [CAM_HOLE_SPACING_W / 2, 0, -CAM_HOLE_SPACING_H / 2],
    [-CAM_HOLE_SPACING_W / 2, 0, CAM_HOLE_SPACING_H / 2],
    [CAM_HOLE_SPACING_W / 2, 0, CAM_HOLE_SPACING_H / 2]
  ].map(([x, y, z]) =>
    translate([x, INT_D / 2 + WALL + CAM_POCKET_DEPTH - 2, z + 2],
      rotate([Math.PI / 2, 0, 0],
        cyl(CAM_MOUNT_HOLE / 2, WALL * 3)
      )
    )
  );

  // Camera pocket — REAR (negative Y wall) — mirror of front
  const rearCamPocket = translate([0, -(INT_D / 2 + WALL + CAM_POCKET_DEPTH / 2 - 1), 2],
    rotate([-Math.PI * CAM_ANGLE / 180, 0, 0],
      cuboid({ size: [CAM_W + TOL * 2, CAM_POCKET_DEPTH, CAM_D + TOL * 2] })
    )
  );

  const rearLens = translate([0, -(EXT_D / 2), 2],
    rotate([-(Math.PI / 2 + Math.PI * CAM_ANGLE / 180), 0, 0],
      cyl(LENS_DIA / 2 + 1.5, WALL * 4)
    )
  );

  const rearCamHoles = [
    [-CAM_HOLE_SPACING_W / 2, 0, -CAM_HOLE_SPACING_H / 2],
    [CAM_HOLE_SPACING_W / 2, 0, -CAM_HOLE_SPACING_H / 2],
    [-CAM_HOLE_SPACING_W / 2, 0, CAM_HOLE_SPACING_H / 2],
    [CAM_HOLE_SPACING_W / 2, 0, CAM_HOLE_SPACING_H / 2]
  ].map(([x, y, z]) =>
    translate([x, -(INT_D / 2 + WALL + CAM_POCKET_DEPTH - 2), z + 2],
      rotate([Math.PI / 2, 0, 0],
        cyl(CAM_MOUNT_HOLE / 2, WALL * 3)
      )
    )
  );

  // CSI ribbon cable channels (from Pi to each camera pocket)
  const csiFront = translate([12, INT_D / 2 + WALL / 2, WALL + 2],
    cuboid({ size: [17, WALL + CAM_POCKET_DEPTH + 2, 3] })
  );
  const csiRear = translate([-12, -(INT_D / 2 + WALL / 2), WALL + 2],
    cuboid({ size: [17, WALL + CAM_POCKET_DEPTH + 2, 3] })
  );

  // USB-C power port cutout (left side — Pi's USB-C is on the short edge)
  const usbC = translate([-(EXT_W / 2), 15, WALL + 4],
    cuboid({ size: [WALL * 3, 12, 7] })
  );

  // Cable routing channel (for hardwired 12V power)
  const cableChannel = translate([-(EXT_W / 2), 15, WALL + 10],
    cuboid({ size: [WALL * 3, CABLE_CHAN_W, CABLE_CHAN_H] })
  );

  // microSD slot (right side of Pi)
  const sdSlot = translate([EXT_W / 2, -20, WALL + 2],
    cuboid({ size: [WALL * 3, SD_SLOT_W, SD_SLOT_H] })
  );

  // Power button access hole (top of Pi 5)
  const pwrBtn = translate([35, -(EXT_D / 2), WALL + 8],
    rotate([Math.PI / 2, 0, 0],
      cyl(PWR_BTN_DIA / 2, WALL * 3)
    )
  );

  // Status LED window (Pi activity LED)
  const statusLED = translate([30, -(EXT_D / 2), WALL + 4],
    cuboid({ size: [STATUS_LED_W, WALL * 3, STATUS_LED_H] })
  );

  // Recording indicator LED hole (front face, visible from outside)
  const recLED = translate([15, EXT_D / 2, 10],
    rotate([Math.PI / 2, 0, 0],
      cyl(LED_DIA / 2, WALL * 3)
    )
  );

  // Side ventilation (both long sides)
  const sideVentsLeft = translate([-(EXT_W / 2), 0, SPLIT_H / 2 - 2],
    rotate([0, Math.PI / 2, 0],
      ventGrid(1, 6, 2, 5, 0, 3.5, WALL)
    )
  );
  const sideVentsRight = translate([EXT_W / 2, 0, SPLIT_H / 2 - 2],
    rotate([0, Math.PI / 2, 0],
      ventGrid(1, 6, 2, 5, 0, 3.5, WALL)
    )
  );

  // Pi mounting posts (5mm standoffs from floor)
  const piPosts = PI_HOLES.map(([x, y]) =>
    translate([
      x - INT_W / 2 + TOL,
      y - INT_D / 2 + TOL,
      -(SPLIT_H / 2) + WALL
    ],
      post(0, 0, 5, PI_MOUNT_HOLE / 2, 3)
    )
  );

  // Snap-fit ledge (rim for top half to sit on)
  const snapLedge = subtract(
    translate([0, 0, SPLIT_H / 2 - 1],
      cuboid({ size: [INT_W + 2, INT_D + 2, 2] })
    ),
    translate([0, 0, SPLIT_H / 2 - 1],
      cuboid({ size: [INT_W - 2, INT_D - 2, 3] })
    )
  );

  // Build bottom
  let bottom = subtract(outer, inner);
  bottom = subtract(bottom, frontCamPocket, frontLens, ...frontCamHoles);
  bottom = subtract(bottom, rearCamPocket, rearLens, ...rearCamHoles);
  bottom = subtract(bottom, csiFront, csiRear);
  bottom = subtract(bottom, usbC, cableChannel, sdSlot);
  bottom = subtract(bottom, pwrBtn, statusLED, recLED);
  bottom = subtract(bottom, sideVentsLeft, sideVentsRight);
  bottom = union(bottom, ...piPosts, snapLedge);

  return translate([0, 0, SPLIT_H / 2],
    colorize([0.15, 0.15, 0.15, 0.9], bottom)
  );
}

// -----------------------------------------------------------------------------
// TOP HALF (LID)
// -----------------------------------------------------------------------------

function topHalf() {
  // Outer shell — top half
  let outer = rbox(EXT_W, EXT_D, SPLIT_H, CORNER_R);

  // Inner cavity
  const inner = translate([0, 0, -WALL],
    cuboid({ size: [INT_W, INT_D, SPLIT_H] })
  );

  // 30mm fan cutout (centered on top, over AI HAT)
  const fanHole = translate([0, 0, SPLIT_H / 2],
    cyl(FAN_SIZE / 2 - 2, WALL * 3)
  );

  // Fan mount screw holes
  const fanScrews = [
    [FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2],
    [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2],
    [FAN_HOLE_SPACING / 2, -FAN_HOLE_SPACING / 2],
    [-FAN_HOLE_SPACING / 2, -FAN_HOLE_SPACING / 2]
  ].map(([x, y]) =>
    translate([x, y, SPLIT_H / 2],
      cyl(FAN_MOUNT_HOLE / 2, WALL * 3)
    )
  );

  // Fan intake grid (honeycomb-ish pattern around fan)
  const fanVents = translate([0, 0, SPLIT_H / 2],
    ventGrid(4, 4, 2, 3, 4, 4, WALL)
  );

  // GPS module mount area (top surface, offset from fan)
  // GPS needs sky view — mount on top with antenna facing up
  const gpsRecess = translate([-(EXT_W / 4), 0, SPLIT_H / 2 - GPS_H / 2],
    cuboid({ size: [GPS_W + TOL * 2, GPS_D + TOL * 2, GPS_H + 1] })
  );

  // GPS antenna window (thinned wall for signal, not full cutout)
  const gpsWindow = translate([-(EXT_W / 4), 0, SPLIT_H / 2],
    cuboid({ size: [GPS_W - 4, GPS_D - 4, WALL] }) // leave 0.5mm floor
  );

  // GPS mount holes (M3)
  const gpsHoles = [
    [-(GPS_W / 2 - 2), -(GPS_D / 2 - 2)],
    [(GPS_W / 2 - 2), -(GPS_D / 2 - 2)],
    [-(GPS_W / 2 - 2), (GPS_D / 2 - 2)],
    [(GPS_W / 2 - 2), (GPS_D / 2 - 2)]
  ].map(([x, y]) =>
    translate([x - EXT_W / 4, y, SPLIT_H / 2 - GPS_H],
      cyl(GPS_MOUNT_HOLE / 2, GPS_H + WALL + 2)
    )
  );

  // Snap-fit inner rim (mates with bottom ledge)
  const snapRim = subtract(
    translate([0, 0, -(SPLIT_H / 2) + 1],
      cuboid({ size: [INT_W, INT_D, 2.5] })
    ),
    translate([0, 0, -(SPLIT_H / 2) + 1],
      cuboid({ size: [INT_W - 3, INT_D - 3, 3.5] })
    )
  );

  // Snap tabs (flexible clips on each side)
  const snapTabs = SNAP_POSITIONS.map(xPos =>
    translate([xPos, INT_D / 2, -(SPLIT_H / 2) + 1],
      cuboid({ size: [SNAP_W, SNAP_DEPTH, SNAP_H] })
    )
  );
  const snapTabsMirror = SNAP_POSITIONS.map(xPos =>
    translate([xPos, -(INT_D / 2), -(SPLIT_H / 2) + 1],
      cuboid({ size: [SNAP_W, SNAP_DEPTH, SNAP_H] })
    )
  );

  // Camera pocket extensions in top half (matching bottom)
  const frontCamTop = translate([0, INT_D / 2 + WALL + CAM_POCKET_DEPTH / 2 - 1, -2],
    rotate([Math.PI * CAM_ANGLE / 180, 0, 0],
      cuboid({ size: [CAM_W + TOL * 2, CAM_POCKET_DEPTH, CAM_D + TOL * 2] })
    )
  );
  const rearCamTop = translate([0, -(INT_D / 2 + WALL + CAM_POCKET_DEPTH / 2 - 1), -2],
    rotate([-Math.PI * CAM_ANGLE / 180, 0, 0],
      cuboid({ size: [CAM_W + TOL * 2, CAM_POCKET_DEPTH, CAM_D + TOL * 2] })
    )
  );

  // Windshield mount integrated on top
  const mountBase = translate([0, 0, SPLIT_H / 2 + MOUNT_H / 2 - 0.5],
    rbox(MOUNT_W, MOUNT_D, MOUNT_H, 2)
  );

  // Mount attachment slot (for adhesive pad or suction cup arm)
  const mountSlot = translate([0, 0, SPLIT_H / 2 + MOUNT_H / 2],
    cuboid({ size: [MOUNT_SLOT_W, MOUNT_SLOT_D, MOUNT_H + 2] })
  );

  // 1/4-20 threaded insert hole (standard camera/dashcam mount)
  const quarterTwenty = translate([0, 0, SPLIT_H / 2],
    cyl(3.1, MOUNT_H + WALL + 2) // 6.2mm hole for 1/4-20 insert
  );

  // Build top
  let top = subtract(outer, inner);
  top = subtract(top, fanHole, ...fanScrews, fanVents);
  top = subtract(top, gpsRecess, gpsWindow, ...gpsHoles);
  top = subtract(top, frontCamTop, rearCamTop);
  top = union(top, snapRim, ...snapTabs, ...snapTabsMirror);
  top = union(top, mountBase);
  top = subtract(top, mountSlot, quarterTwenty);

  return translate([0, 0, SPLIT_H + SPLIT_H / 2 + 0.5], // float above bottom for preview
    colorize([0.2, 0.2, 0.2, 0.85], top)
  );
}

// -----------------------------------------------------------------------------
// ASSEMBLY
// -----------------------------------------------------------------------------

function main() {
  return [
    bottomHalf(),
    topHalf()
  ];
}

module.exports = { main };
