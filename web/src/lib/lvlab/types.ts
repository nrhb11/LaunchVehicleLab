export type PropellantName = "KEROLOX" | "METHALOX" | "HYDROLOX";

export interface PropellantSpec {
  name: string;
  densityKgPerM3: number;
}

export interface PropellantCombination {
  key: PropellantName;
  name: string;
  oxidizer: PropellantSpec;
  fuel: PropellantSpec;
  mixtureRatioOf: number;
  seaLevelIspS: number;
  vacuumIspS: number;
}

export interface MissionSpec {
  payloadMassKg: number;
  altitudeM: number;
  launchLatitudeRad: number;
}

export interface DeltaVBudget {
  orbitalVelocity: number;
  earthRotationBoost: number;
  netIdealBurn: number;
  gravityLoss: number;
  dragLoss: number;
  steeringLoss: number;
  margin: number;
  totalDeltaV: number;
}

export interface StageSizingResult {
  name: string;
  deltaV: number;
  propellantMassKg: number;
  structuralMassKg: number;
  burnoutMassKg: number;
  initialMassKg: number;
  massRatio: number;
}

export interface TankGeometry {
  diameterM: number;
  cylinderLengthM: number;
  domeHeightM: number;
  totalLengthM: number;
  volumeM3: number;
  surfaceAreaM2: number;
}

export interface StageGeometry {
  diameterM: number;
  totalLengthM: number;
  oxidizerTank: TankGeometry;
  fuelTank: TankGeometry;
  intertankLengthM: number;
  skirtLengthM: number;
}

export interface FairingGeometry {
  diameterM: number;
  totalLengthM: number;
  cylinderLengthM: number;
  noseConeLengthM: number;
  surfaceAreaM2: number;
  internalVolumeM3: number;
}

export interface VehicleGeometry {
  fairing: FairingGeometry;
  stage2: StageGeometry;
  interstageLengthM: number;
  stage1: StageGeometry;
  totalLengthM: number;
  finenessRatio: number;
}

export interface SubsystemMassBreakdown {
  tanksMassKg: number;
  propulsionMassKg: number;
  avionicsMassKg: number;
  interstageMassKg: number;
  fairingMassKg: number;
  residualsKg: number;
  totalDryMassKg: number;
}

export interface CoupledStageResult {
  name: string;
  propellant: PropellantCombination;
  propellantMassKg: number;
  oxidizerMassKg: number;
  fuelMassKg: number;
  sizing: StageSizingResult;
  geometry: StageGeometry;
  mass: SubsystemMassBreakdown;
  structuralFraction: number;
}

export interface CoupledVehicleResult {
  mission: MissionSpec;
  deltaV: DeltaVBudget;
  geometry: VehicleGeometry;
  stage1: CoupledStageResult;
  stage2: CoupledStageResult;
  glowKg: number;
  payloadRatioPercent: number;
  iterations: number;
}

export interface TrajectoryPoint {
  timeS: number;
  altitudeM: number;
  downrangeM: number;
  velocity: number;
  flightPathAngleRad: number;
  massKg: number;
  thrustN: number;
  dynamicPressurePa: number;
  mach: number;
  accelerationG: number;
}

export interface FlightEvent {
  name: string;
  timeS: number;
  altitudeM: number;
  velocity: number;
  description: string;
}

export interface TrajectoryResult {
  points: TrajectoryPoint[];
  events: FlightEvent[];
  maxQPa: number;
  maxQTimeS: number;
  maxQAltM: number;
  maxAccelerationG: number;
  finalAltitudeM: number;
  finalVelocity: number;
  totalFlightTimeS: number;
}

export interface AtmosphereState {
  altitudeM: number;
  temperatureK: number;
  pressurePa: number;
  densityKgPerM3: number;
  speedOfSound: number;
}

export interface DesignInputs {
  payloadKg: number;
  altitudeKm: number;
  latitudeDeg: number;
  stage1Prop: PropellantName;
  stage2Prop: PropellantName;
  stage1DiameterM: number;
  stage2DiameterM: number;
}
