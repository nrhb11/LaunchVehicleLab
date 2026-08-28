import type {
  AtmosphereState,
  CoupledStageResult,
  CoupledVehicleResult,
  DeltaVBudget,
  DesignInputs,
  FairingGeometry,
  FlightEvent,
  MissionSpec,
  PropellantCombination,
  PropellantName,
  StageGeometry,
  StageSizingResult,
  SubsystemMassBreakdown,
  TankGeometry,
  TrajectoryPoint,
  TrajectoryResult,
  VehicleGeometry,
} from "./types";

export const G0 = 9.80665;
export const EARTH_MU = 3.986004418e14;
export const EARTH_RADIUS = 6_378_137;
export const EARTH_OMEGA = 7.292115e-5;
export const AIR_R = 287.05287;
export const AIR_GAMMA = 1.4;
export const GEO_RADIUS = 6_356_766;

const LOX = { name: "Liquid Oxygen", densityKgPerM3: 1141 };
const RP1 = { name: "RP-1 Kerosene", densityKgPerM3: 810 };
const CH4 = { name: "Liquid Methane", densityKgPerM3: 422.6 };
const LH2 = { name: "Liquid Hydrogen", densityKgPerM3: 70.85 };

export const PROPELLANTS: Record<PropellantName, PropellantCombination> = {
  KEROLOX: {
    key: "KEROLOX",
    name: "Kerolox (LOX / RP-1)",
    oxidizer: LOX,
    fuel: RP1,
    mixtureRatioOf: 2.56,
    seaLevelIspS: 300,
    vacuumIspS: 325,
  },
  METHALOX: {
    key: "METHALOX",
    name: "Methalox (LOX / LCH4)",
    oxidizer: LOX,
    fuel: CH4,
    mixtureRatioOf: 3.5,
    seaLevelIspS: 330,
    vacuumIspS: 365,
  },
  HYDROLOX: {
    key: "HYDROLOX",
    name: "Hydrolox (LOX / LH2)",
    oxidizer: LOX,
    fuel: LH2,
    mixtureRatioOf: 5.5,
    seaLevelIspS: 380,
    vacuumIspS: 450,
  },
};

const ATM_LAYERS: [number, number, number, number][] = [
  [0, 288.15, 101325, -0.0065],
  [11000, 216.65, 22632.06, 0],
  [20000, 216.65, 5474.889, 0.001],
  [32000, 228.65, 868.0187, 0.0028],
  [47000, 270.65, 110.9063, 0],
  [51000, 270.65, 66.93887, -0.0028],
  [71000, 214.65, 3.95642, -0.002],
];

export function circularOrbitVelocity(altitudeM: number): number {
  return Math.sqrt(EARTH_MU / (EARTH_RADIUS + altitudeM));
}

export function earthRotationBoost(latRad: number, azimuthRad = Math.PI / 2): number {
  return EARTH_OMEGA * EARTH_RADIUS * Math.cos(latRad) * Math.sin(azimuthRad);
}

export function calculateDeltaVBudget(mission: MissionSpec): DeltaVBudget {
  const gravityLoss = 1200;
  const dragLoss = 150;
  const steeringLoss = 200;
  const orbitalVelocity = circularOrbitVelocity(mission.altitudeM);
  const boost = earthRotationBoost(mission.launchLatitudeRad);
  const netIdealBurn = orbitalVelocity - boost;
  const losses = gravityLoss + dragLoss + steeringLoss;
  const subtotal = netIdealBurn + losses;
  const margin = subtotal * 0.03;
  return {
    orbitalVelocity,
    earthRotationBoost: boost,
    netIdealBurn,
    gravityLoss,
    dragLoss,
    steeringLoss,
    margin,
    totalDeltaV: subtotal + margin,
  };
}

function stepGrowth(deltaV: number, cEff: number, eps: number): number {
  const ratio = Math.exp(deltaV / cEff);
  const denom = 1 - eps * ratio;
  if (denom <= 0) return Number.POSITIVE_INFINITY;
  return ((1 - eps) * ratio) / denom;
}

function optimizeTwoStage(
  payloadKg: number,
  targetDv: number,
  isp1: number,
  eps1: number,
  isp2: number,
  eps2: number,
): { stage1: StageSizingResult; stage2: StageSizingResult; glowKg: number } {
  const c1 = G0 * isp1;
  const c2 = G0 * isp2;
  const dv1Max = c1 * Math.log(1 / eps1);
  const dv2Max = c2 * Math.log(1 / eps2);
  if (targetDv >= dv1Max + dv2Max) {
    throw new Error(
      `Target ΔV (${targetDv.toFixed(0)} m/s) exceeds combined limit (${(dv1Max + dv2Max).toFixed(0)} m/s).`,
    );
  }
  let a = Math.max(1e-3, targetDv - dv2Max + 1e-3);
  let b = Math.min(targetDv - 1e-3, dv1Max - 1e-3);
  if (a >= b) throw new Error("No feasible two-stage design space for this ΔV.");

  const invphi = (Math.sqrt(5) - 1) / 2;
  const invphi2 = (3 - Math.sqrt(5)) / 2;
  const objective = (dv1: number) =>
    stepGrowth(dv1, c1, eps1) * stepGrowth(targetDv - dv1, c2, eps2);

  let h = b - a;
  let c = a + invphi2 * h;
  let d = a + invphi * h;
  let yc = objective(c);
  let yd = objective(d);
  for (let i = 0; i < 80; i++) {
    if (yc < yd) {
      b = d;
      d = c;
      yd = yc;
      h = invphi * h;
      c = a + invphi2 * h;
      yc = objective(c);
    } else {
      a = c;
      c = d;
      yc = yd;
      h = invphi * h;
      d = a + invphi * h;
      yd = objective(d);
    }
  }

  const dv1 = (a + b) / 2;
  const dv2 = targetDv - dv1;
  const x1 = stepGrowth(dv1, c1, eps1);
  const x2 = stepGrowth(dv2, c2, eps2);

  const mInitial2 = x2 * payloadKg;
  const mLoaded2 = mInitial2 - payloadKg;
  const mStruct2 = eps2 * mLoaded2;
  const mProp2 = (1 - eps2) * mLoaded2;
  const mBurnout2 = mStruct2 + payloadKg;

  const mInitial1 = x1 * mInitial2;
  const mLoaded1 = mInitial1 - mInitial2;
  const mStruct1 = eps1 * mLoaded1;
  const mProp1 = (1 - eps1) * mLoaded1;
  const mBurnout1 = mStruct1 + mInitial2;

  return {
    glowKg: mInitial1,
    stage1: {
      name: "Stage 1",
      deltaV: dv1,
      propellantMassKg: mProp1,
      structuralMassKg: mStruct1,
      burnoutMassKg: mBurnout1,
      initialMassKg: mInitial1,
      massRatio: mInitial1 / mBurnout1,
    },
    stage2: {
      name: "Stage 2",
      deltaV: dv2,
      propellantMassKg: mProp2,
      structuralMassKg: mStruct2,
      burnoutMassKg: mBurnout2,
      initialMassKg: mInitial2,
      massRatio: mInitial2 / mBurnout2,
    },
  };
}

function sizeTank(massKg: number, density: number, diameterM: number, ullage = 0.04): TankGeometry {
  const radius = diameterM / 2;
  const cross = Math.PI * radius * radius;
  const domeHeight = diameterM / 4;
  const required = (massKg / density) * (1 + ullage);
  const twoDomes = (Math.PI * diameterM ** 3) / 12;
  let cylinderLength = 0;
  let volume = twoDomes;
  if (required > twoDomes) {
    cylinderLength = (required - twoDomes) / cross;
    volume = required;
  }
  const e = Math.sqrt(3) / 2;
  const atanhE = 0.5 * Math.log((1 + e) / (1 - e));
  const domeArea = 0.5 * Math.PI * radius * radius * (1 + ((1 - e * e) / e) * atanhE);
  return {
    diameterM,
    cylinderLengthM: cylinderLength,
    domeHeightM: domeHeight,
    totalLengthM: cylinderLength + 2 * domeHeight,
    volumeM3: volume,
    surfaceAreaM2: 2 * domeArea + 2 * Math.PI * radius * cylinderLength,
  };
}

function sizeStage(propellantKg: number, combo: PropellantCombination, diameterM: number): StageGeometry {
  const mr = combo.mixtureRatioOf;
  const mOx = propellantKg * (mr / (1 + mr));
  const mFuel = propellantKg * (1 / (1 + mr));
  const oxTank = sizeTank(mOx, combo.oxidizer.densityKgPerM3, diameterM);
  const fuelTank = sizeTank(mFuel, combo.fuel.densityKgPerM3, diameterM);
  const intertank = 0.3;
  const skirt = 0.8 * diameterM;
  return {
    diameterM,
    totalLengthM: oxTank.totalLengthM + fuelTank.totalLengthM + intertank + skirt,
    oxidizerTank: oxTank,
    fuelTank,
    intertankLengthM: intertank,
    skirtLengthM: skirt,
  };
}

function sizeFairing(diameterM: number): FairingGeometry {
  const cyl = 1.8;
  const nose = 1.2 * diameterM;
  const radius = diameterM / 2;
  const slant = Math.sqrt(nose * nose + radius * radius);
  return {
    diameterM,
    totalLengthM: cyl + nose,
    cylinderLengthM: cyl,
    noseConeLengthM: nose,
    surfaceAreaM2: Math.PI * radius * slant + 2 * Math.PI * radius * cyl,
    internalVolumeM3: Math.PI * radius * radius * cyl + (Math.PI * radius * radius * nose) / 3,
  };
}

function estimateFairingMass(fairing: FairingGeometry): number {
  return fairing.surfaceAreaM2 * 10.5 * 1.2;
}

function estimateStageMass(
  geom: StageGeometry,
  propellantKg: number,
  initialKg: number,
  tw: number,
  engineTw: number,
  avionics: number,
  interstage = 0,
): SubsystemMassBreakdown {
  const oxA = geom.oxidizerTank.surfaceAreaM2;
  const fuelA = geom.fuelTank.surfaceAreaM2;
  const skirtA = Math.PI * geom.diameterM * (geom.intertankLengthM + geom.skirtLengthM);
  const tanks = (oxA + fuelA + skirtA) * 15;
  const thrustN = initialKg * G0 * tw;
  const propulsion = (thrustN / (G0 * engineTw)) * 1.25;
  const residuals = propellantKg * 0.012;
  const totalDry = tanks + propulsion + avionics + interstage + residuals;
  return {
    tanksMassKg: tanks,
    propulsionMassKg: propulsion,
    avionicsMassKg: avionics,
    interstageMassKg: interstage,
    fairingMassKg: 0,
    residualsKg: residuals,
    totalDryMassKg: totalDry,
  };
}

export function runCoupledSizing(inputs: DesignInputs): CoupledVehicleResult {
  const mission: MissionSpec = {
    payloadMassKg: inputs.payloadKg,
    altitudeM: inputs.altitudeKm * 1000,
    launchLatitudeRad: (inputs.latitudeDeg * Math.PI) / 180,
  };
  const s1Combo = PROPELLANTS[inputs.stage1Prop];
  const s2Combo = PROPELLANTS[inputs.stage2Prop];
  const budget = calculateDeltaVBudget(mission);
  const fairing = sizeFairing(inputs.stage2DiameterM);
  const fairingMass = estimateFairingMass(fairing);
  const effectivePayload = mission.payloadMassKg + fairingMass;

  let eps1 = 0.08;
  let eps2 = 0.1;
  let prevGlow = 0;
  let iterations = 0;
  let staging = optimizeTwoStage(
    effectivePayload,
    budget.totalDeltaV,
    s1Combo.seaLevelIspS,
    eps1,
    s2Combo.vacuumIspS,
    eps2,
  );
  let s1Geom = sizeStage(staging.stage1.propellantMassKg, s1Combo, inputs.stage1DiameterM);
  let s2Geom = sizeStage(staging.stage2.propellantMassKg, s2Combo, inputs.stage2DiameterM);
  let s1Mass = estimateStageMass(s1Geom, staging.stage1.propellantMassKg, staging.glowKg, 1.3, 80, 35, 35);
  let s2Mass = estimateStageMass(s2Geom, staging.stage2.propellantMassKg, staging.stage2.initialMassKg, 0.85, 65, 45);

  for (let i = 1; i <= 40; i++) {
    iterations = i;
    staging = optimizeTwoStage(
      effectivePayload,
      budget.totalDeltaV,
      s1Combo.seaLevelIspS,
      eps1,
      s2Combo.vacuumIspS,
      eps2,
    );
    s1Geom = sizeStage(staging.stage1.propellantMassKg, s1Combo, inputs.stage1DiameterM);
    s2Geom = sizeStage(staging.stage2.propellantMassKg, s2Combo, inputs.stage2DiameterM);
    s2Mass = estimateStageMass(s2Geom, staging.stage2.propellantMassKg, staging.stage2.initialMassKg, 0.85, 65, 45);
    s1Mass = estimateStageMass(s1Geom, staging.stage1.propellantMassKg, staging.glowKg, 1.3, 80, 35, 35);
    const newEps1 = s1Mass.totalDryMassKg / (s1Mass.totalDryMassKg + staging.stage1.propellantMassKg);
    const newEps2 = s2Mass.totalDryMassKg / (s2Mass.totalDryMassKg + staging.stage2.propellantMassKg);
    const glowDiff = Math.abs(staging.glowKg - prevGlow);
    const epsDiff = Math.max(Math.abs(newEps1 - eps1), Math.abs(newEps2 - eps2));
    if (i > 1 && glowDiff < 0.5 && epsDiff < 1e-4) break;
    prevGlow = staging.glowKg;
    eps1 = 0.5 * eps1 + 0.5 * newEps1;
    eps2 = 0.5 * eps2 + 0.5 * newEps2;
  }

  const totalLength =
    fairing.totalLengthM + s2Geom.totalLengthM + 0.8 + s1Geom.totalLengthM;
  const geometry: VehicleGeometry = {
    fairing,
    stage2: s2Geom,
    interstageLengthM: 0.8,
    stage1: s1Geom,
    totalLengthM: totalLength,
    finenessRatio: totalLength / s1Geom.diameterM,
  };

  const s1Mr = s1Combo.mixtureRatioOf;
  const s2Mr = s2Combo.mixtureRatioOf;
  const stage1: CoupledStageResult = {
    name: "Stage 1 booster",
    propellant: s1Combo,
    propellantMassKg: staging.stage1.propellantMassKg,
    oxidizerMassKg: staging.stage1.propellantMassKg * (s1Mr / (1 + s1Mr)),
    fuelMassKg: staging.stage1.propellantMassKg * (1 / (1 + s1Mr)),
    sizing: staging.stage1,
    geometry: s1Geom,
    mass: s1Mass,
    structuralFraction: s1Mass.totalDryMassKg / (s1Mass.totalDryMassKg + staging.stage1.propellantMassKg),
  };
  const stage2: CoupledStageResult = {
    name: "Stage 2 upper",
    propellant: s2Combo,
    propellantMassKg: staging.stage2.propellantMassKg,
    oxidizerMassKg: staging.stage2.propellantMassKg * (s2Mr / (1 + s2Mr)),
    fuelMassKg: staging.stage2.propellantMassKg * (1 / (1 + s2Mr)),
    sizing: staging.stage2,
    geometry: s2Geom,
    mass: s2Mass,
    structuralFraction: s2Mass.totalDryMassKg / (s2Mass.totalDryMassKg + staging.stage2.propellantMassKg),
  };

  return {
    mission,
    deltaV: budget,
    geometry,
    stage1,
    stage2,
    glowKg: staging.glowKg,
    payloadRatioPercent: (mission.payloadMassKg / staging.glowKg) * 100,
    iterations,
  };
}

export function atmosphere1976(altitudeM: number): AtmosphereState {
  const h = Math.max(0, altitudeM);
  const H = (GEO_RADIUS * h) / (GEO_RADIUS + h);
  if (H >= 84852) {
    const t = 186.87;
    const scale = (AIR_R * t) / G0;
    const p = 0.3734 * Math.exp(-(H - 84852) / scale);
    return {
      altitudeM: h,
      temperatureK: t,
      pressurePa: p,
      densityKgPerM3: p / (AIR_R * t),
      speedOfSound: Math.sqrt(AIR_GAMMA * AIR_R * t),
    };
  }
  let layer = ATM_LAYERS[0];
  for (const candidate of ATM_LAYERS) {
    if (H >= candidate[0]) layer = candidate;
    else break;
  }
  const [hb, tb, pb, lb] = layer;
  const dh = H - hb;
  let temperature = tb;
  let pressure = pb;
  if (Math.abs(lb) < 1e-12) {
    pressure = pb * Math.exp(-(G0 * dh) / (AIR_R * tb));
  } else {
    temperature = tb + lb * dh;
    pressure = pb * (temperature / tb) ** (-G0 / (AIR_R * lb));
  }
  return {
    altitudeM: h,
    temperatureK: temperature,
    pressurePa: pressure,
    densityKgPerM3: pressure / (AIR_R * temperature),
    speedOfSound: Math.sqrt(AIR_GAMMA * AIR_R * temperature),
  };
}

export function dragCoefficient(mach: number): number {
  const sub = 0.22;
  const peak = 0.48;
  const hyp = 0.2;
  if (mach < 0.8) return sub;
  if (mach <= 1.2) {
    const p = (mach - 0.8) / 0.4;
    return sub + (peak - sub) * Math.sin((p * Math.PI) / 2) ** 2;
  }
  const decay = 1 + 0.75 * (mach - 1.2);
  return hyp + (peak - hyp) / decay;
}

export function simulateAscent(vehicle: CoupledVehicleResult): TrajectoryResult {
  const pitchKick = 12;
  const pitchEndDeg = 25;
  const sepDelay = 2.5;
  const dt = 0.15;
  const s1 = vehicle.stage1;
  const s2 = vehicle.stage2;
  const targetAlt = vehicle.mission.altitudeM;
  const rTarget = EARTH_RADIUS + targetAlt;
  const refArea = (Math.PI * s1.geometry.diameterM ** 2) / 4;
  const glow = vehicle.glowKg;
  const f1 = glow * G0 * 1.3;
  const mDot1 = f1 / (G0 * s1.propellant.seaLevelIspS);
  const tBurn1 = s1.propellantMassKg / mDot1;
  const f2 = s2.sizing.initialMassKg * G0 * 0.85;
  const tBurn2 = s2.propellantMassKg / (f2 / (G0 * s2.propellant.vacuumIspS));

  let r = EARTH_RADIUS;
  let x = 0;
  let vr = 0.5;
  let vx = 0;
  let m = glow;
  let t = 0;

  const points: TrajectoryPoint[] = [];
  const events: FlightEvent[] = [
    { name: "Liftoff", timeS: 0, altitudeM: 0, velocity: 0, description: "Vehicle leaves the pad." },
  ];

  let maxQ = 0;
  let maxQt = 0;
  let maxQAlt = 0;
  let maxQG = 0;
  let maxQV = 0;
  let transonic = false;
  let kicked = false;
  let fairingOff = false;
  let sample = 0;

  const deriv = (
    cr: number,
    cvr: number,
    cvx: number,
    cm: number,
    thrust: number,
    isp: number,
    theta: number,
  ) => {
    const h = Math.max(0, cr - EARTH_RADIUS);
    const v = Math.sqrt(cvr * cvr + cvx * cvx);
    const vSafe = Math.max(0.1, v);
    const atm = atmosphere1976(h);
    const q = 0.5 * atm.densityKgPerM3 * v * v;
    const mach = v / Math.max(1, atm.speedOfSound);
    const dForce = q * refArea * dragCoefficient(mach);
    const gLocal = EARTH_MU / (cr * cr);
    const dragR = dForce * (cvr / vSafe);
    const dragX = dForce * (cvx / vSafe);
    return {
      dr: cvr,
      dx: (EARTH_RADIUS / cr) * cvx,
      dvr: (thrust * Math.sin(theta) - dragR) / cm - gLocal + (cvx * cvx) / cr,
      dvx: (thrust * Math.cos(theta) - dragX) / cm - (cvr * cvx) / cr,
      dm: thrust > 0 ? -(thrust / (G0 * isp)) : 0,
    };
  };

  const stepRk4 = (thrust: number, isp: number, theta: number) => {
    const k1 = deriv(r, vr, vx, m, thrust, isp, theta);
    const k2 = deriv(
      r + 0.5 * dt * k1.dr,
      vr + 0.5 * dt * k1.dvr,
      vx + 0.5 * dt * k1.dvx,
      m + 0.5 * dt * k1.dm,
      thrust,
      isp,
      theta,
    );
    const k3 = deriv(
      r + 0.5 * dt * k2.dr,
      vr + 0.5 * dt * k2.dvr,
      vx + 0.5 * dt * k2.dvx,
      m + 0.5 * dt * k2.dm,
      thrust,
      isp,
      theta,
    );
    const k4 = deriv(r + dt * k3.dr, vr + dt * k3.dvr, vx + dt * k3.dvx, m + dt * k3.dm, thrust, isp, theta);
    r += (dt / 6) * (k1.dr + 2 * k2.dr + 2 * k3.dr + k4.dr);
    x += (dt / 6) * (k1.dx + 2 * k2.dx + 2 * k3.dx + k4.dx);
    vr += (dt / 6) * (k1.dvr + 2 * k2.dvr + 2 * k3.dvr + k4.dvr);
    vx += (dt / 6) * (k1.dvx + 2 * k2.dvx + 2 * k3.dvx + k4.dvx);
    m += (dt / 6) * (k1.dm + 2 * k2.dm + 2 * k3.dm + k4.dm);
    t += dt;
    sample += dt;
  };

  const samplePoint = (thrust: number) => {
    const h = Math.max(0, r - EARTH_RADIUS);
    const v = Math.sqrt(vr * vr + vx * vx);
    const atm = atmosphere1976(h);
    const q = 0.5 * atm.densityKgPerM3 * v * v;
    const mach = v / Math.max(1, atm.speedOfSound);
    const dForce = q * refArea * dragCoefficient(mach);
    const accelG = ((thrust - dForce) / m) / G0;
    points.push({
      timeS: round(t, 2),
      altitudeM: round(h, 1),
      downrangeM: round(x, 1),
      velocity: round(v, 2),
      flightPathAngleRad: round(Math.atan2(vr, Math.max(0.001, vx)), 4),
      massKg: round(m, 1),
      thrustN: round(thrust, 1),
      dynamicPressurePa: round(q, 1),
      mach: round(mach, 2),
      accelerationG: round(accelG, 2),
    });
  };

  while (t < tBurn1) {
    const h = Math.max(0, r - EARTH_RADIUS);
    const v = Math.sqrt(vr * vr + vx * vx);
    const atm = atmosphere1976(h);
    const q = 0.5 * atm.densityKgPerM3 * v * v;
    const mach = v / Math.max(1, atm.speedOfSound);
    const dForce = q * refArea * dragCoefficient(mach);
    if (!transonic && mach >= 1) {
      transonic = true;
      events.push({
        name: "Transonic (Mach 1)",
        timeS: round(t, 2),
        altitudeM: round(h, 1),
        velocity: round(v, 1),
        description: `Mach 1 at ${(h / 1000).toFixed(1)} km.`,
      });
    }
    if (q > maxQ) {
      maxQ = q;
      maxQt = t;
      maxQAlt = h;
      maxQV = v;
    }
    let theta = Math.PI / 2;
    if (t >= pitchKick) {
      if (!kicked) {
        kicked = true;
        events.push({
          name: "Pitchover",
          timeS: round(t, 2),
          altitudeM: round(h, 1),
          velocity: round(v, 1),
          description: "Gravity-turn pitch program starts.",
        });
      }
      const prog = (t - pitchKick) / (tBurn1 - pitchKick);
      theta = ((90 - (90 - pitchEndDeg) * prog ** 0.65) * Math.PI) / 180;
    }
    const accelG = ((f1 - dForce) / m) / G0;
    if (accelG > maxQG) maxQG = accelG;
    if (sample >= 1 || t === 0) {
      sample = 0;
      samplePoint(f1);
    }
    stepRk4(f1, s1.propellant.seaLevelIspS, theta);
  }

  events.push({
    name: "Max-Q",
    timeS: round(maxQt, 2),
    altitudeM: round(maxQAlt, 1),
    velocity: round(maxQV, 1),
    description: `Peak dynamic pressure ${(maxQ / 1000).toFixed(1)} kPa at ${(maxQAlt / 1000).toFixed(1)} km.`,
  });

  events.push({
    name: "MECO",
    timeS: round(t, 2),
    altitudeM: round(r - EARTH_RADIUS, 1),
    velocity: round(Math.sqrt(vr * vr + vx * vx), 1),
    description: "Stage 1 main engine cutoff.",
  });

  const tCoastEnd = t + sepDelay;
  while (t < tCoastEnd) {
    const k1 = deriv(r, vr, vx, m, 0, 1, 0);
    r += dt * k1.dr;
    x += dt * k1.dx;
    vr += dt * k1.dvr;
    vx += dt * k1.dvx;
    t += dt;
  }

  m = s2.sizing.initialMassKg;
  events.push({
    name: "Staging",
    timeS: round(t, 2),
    altitudeM: round(r - EARTH_RADIUS, 1),
    velocity: round(Math.sqrt(vr * vr + vx * vx), 1),
    description: "Stage 1 jettisoned. Stage 2 ignites.",
  });

  const tS2Start = t;
  const tS2End = tS2Start + tBurn2;
  while (t < tS2End) {
    const h = Math.max(0, r - EARTH_RADIUS);
    const v = Math.sqrt(vr * vr + vx * vx);
    const atm = atmosphere1976(h);
    const q = 0.5 * atm.densityKgPerM3 * v * v;
    if (!fairingOff && (h >= 100_000 || q < 20)) {
      fairingOff = true;
      const fairingMass = vehicle.geometry.fairing.surfaceAreaM2 * 10.5 * 1.2;
      m = Math.max(s2.sizing.burnoutMassKg, m - fairingMass);
      events.push({
        name: "Fairing jettison",
        timeS: round(t, 2),
        altitudeM: round(h, 1),
        velocity: round(v, 1),
        description: `Payload fairing separated at ${(h / 1000).toFixed(1)} km.`,
      });
    }
    const prog2 = (t - tS2Start) / tBurn2;
    let theta = ((pitchEndDeg * (1 - prog2)) * Math.PI) / 180;
    const altTrim = (rTarget - r) / 80_000 - vr / 1000;
    theta += Math.max(-0.15, Math.min(0.3, altTrim));
    const accelG = f2 / m / G0;
    if (accelG > maxQG) maxQG = accelG;
    if (sample >= 1) {
      sample = 0;
      samplePoint(f2);
    }
    stepRk4(f2, s2.propellant.vacuumIspS, theta);
  }

  const finalAlt = r - EARTH_RADIUS;
  const finalV = Math.sqrt(vr * vr + vx * vx);
  events.push({
    name: "SECO",
    timeS: round(t, 2),
    altitudeM: round(finalAlt, 1),
    velocity: round(finalV, 1),
    description: `Second-engine cutoff. ${(finalAlt / 1000).toFixed(1)} km, ${finalV.toFixed(0)} m/s.`,
  });

  events.sort((a, b) => a.timeS - b.timeS);

  return {
    points,
    events,
    maxQPa: maxQ,
    maxQTimeS: round(maxQt, 2),
    maxQAltM: round(maxQAlt, 1),
    maxAccelerationG: round(maxQG, 2),
    finalAltitudeM: round(finalAlt, 1),
    finalVelocity: round(finalV, 1),
    totalFlightTimeS: round(t, 2),
  };
}

function round(n: number, d: number): number {
  const f = 10 ** d;
  return Math.round(n * f) / f;
}

export function nearestPoint(points: TrajectoryPoint[], timeS: number): TrajectoryPoint | null {
  if (!points.length) return null;
  let best = points[0];
  let bestD = Math.abs(best.timeS - timeS);
  for (const p of points) {
    const d = Math.abs(p.timeS - timeS);
    if (d < bestD) {
      best = p;
      bestD = d;
    }
  }
  return best;
}

export const BENCHMARK: DesignInputs = {
  payloadKg: 500,
  altitudeKm: 500,
  latitudeDeg: 28.5,
  stage1Prop: "KEROLOX",
  stage2Prop: "METHALOX",
  stage1DiameterM: 1.4,
  stage2DiameterM: 1.4,
};
