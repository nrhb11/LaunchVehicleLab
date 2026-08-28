import { create } from "zustand";
import {
  BENCHMARK,
  nearestPoint,
  runCoupledSizing,
  simulateAscent,
} from "@/lib/lvlab/physics";
import type {
  CoupledVehicleResult,
  DesignInputs,
  PropellantName,
  TrajectoryPoint,
  TrajectoryResult,
} from "@/lib/lvlab/types";

function stabilize<T>(value: T): T {
  return JSON.parse(
    JSON.stringify(value, (_key, item) =>
      typeof item === "number" && Number.isFinite(item) ? Math.round(item * 1e6) / 1e6 : item,
    ),
  ) as T;
}

function analyze(inputs: DesignInputs) {
  const vehicle = stabilize(runCoupledSizing(inputs));
  const trajectory = stabilize(simulateAscent(vehicle));
  return {
    vehicle,
    trajectory,
    status: `GLOW ${(vehicle.glowKg / 1000).toFixed(1)} t · ${vehicle.geometry.totalLengthM.toFixed(1)} m · Max-Q ${(trajectory.maxQPa / 1000).toFixed(1)} kPa`,
    error: null as string | null,
  };
}

const initial = analyze(BENCHMARK);

interface StudioState extends DesignInputs {
  vehicle: CoupledVehicleResult | null;
  trajectory: TrajectoryResult | null;
  error: string | null;
  status: string;
  running: boolean;
  flightTime: number;
  playing: boolean;
  playbackSpeed: number;
  setField: <K extends keyof DesignInputs>(key: K, value: DesignInputs[K]) => void;
  setStage1Prop: (name: PropellantName) => void;
  setStage2Prop: (name: PropellantName) => void;
  run: () => void;
  resetBenchmark: () => void;
  setFlightTime: (t: number) => void;
  setPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  currentPoint: () => TrajectoryPoint | null;
}

export const useStudio = create<StudioState>((set, get) => ({
  ...BENCHMARK,
  ...initial,
  running: false,
  flightTime: 0,
  playing: false,
  playbackSpeed: 5,
  setField: (key, value) => set({ [key]: value } as Partial<StudioState>),
  setStage1Prop: (stage1Prop) => set({ stage1Prop }),
  setStage2Prop: (stage2Prop) => set({ stage2Prop }),
  run: () => {
    const { payloadKg, altitudeKm, latitudeDeg, stage1Prop, stage2Prop, stage1DiameterM, stage2DiameterM } =
      get();
    set({ running: true, error: null, status: "Sizing vehicle…", playing: false });
    try {
      const result = analyze({
        payloadKg,
        altitudeKm,
        latitudeDeg,
        stage1Prop,
        stage2Prop,
        stage1DiameterM,
        stage2DiameterM,
      });
      set({
        ...result,
        running: false,
        flightTime: 0,
      });
    } catch (err) {
      set({
        running: false,
        error: err instanceof Error ? err.message : String(err),
        status: "Sizing failed",
      });
    }
  },
  resetBenchmark: () => {
    set({ ...BENCHMARK, playing: false, flightTime: 0, ...analyze(BENCHMARK) });
  },
  setFlightTime: (flightTime) => {
    const total = get().trajectory?.totalFlightTimeS ?? 0;
    set({ flightTime: Math.max(0, Math.min(total, flightTime)) });
  },
  setPlaying: (playing) => set({ playing }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  currentPoint: () => {
    const { trajectory, flightTime } = get();
    if (!trajectory) return null;
    return nearestPoint(trajectory.points, flightTime);
  },
}));
