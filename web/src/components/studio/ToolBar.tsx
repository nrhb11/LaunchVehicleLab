import { Pause, Play, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStudio } from "@/store/studio";

function Readout({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="flex items-baseline gap-1.5 px-2">
      <span className="text-micro uppercase tracking-wider text-subtle">{label}</span>
      <span className="font-mono text-ui tabular text-fg">{value}</span>
      <span className="text-micro text-subtle">{unit}</span>
    </div>
  );
}

export function ToolBar() {
  const run = useStudio((s) => s.run);
  const running = useStudio((s) => s.running);
  const resetBenchmark = useStudio((s) => s.resetBenchmark);
  const playing = useStudio((s) => s.playing);
  const setPlaying = useStudio((s) => s.setPlaying);
  const setFlightTime = useStudio((s) => s.setFlightTime);
  const traj = useStudio((s) => s.trajectory);
  const t = useStudio((s) => s.flightTime);
  const vehicle = useStudio((s) => s.vehicle);

  const glow = vehicle ? (vehicle.glowKg / 1000).toFixed(1) : "—";
  const maxq = traj ? (traj.maxQPa / 1000).toFixed(1) : "—";
  const height = vehicle ? vehicle.geometry.totalLengthM.toFixed(1) : "—";
  const dv = vehicle ? (vehicle.deltaV.totalDeltaV / 1000).toFixed(2) : "—";

  return (
    <div className="flex h-8 shrink-0 items-center gap-1 border-b border-border bg-surface px-2">
      <Button size="xs" onClick={run} disabled={running}>
        {running ? "Computing" : "Size"}
      </Button>
      <Button
        size="icon-sm"
        variant="secondary"
        aria-label={playing ? "Pause" : "Play"}
        onClick={() => {
          if (!traj) return;
          if (t >= (traj.totalFlightTimeS ?? 0)) setFlightTime(0);
          setPlaying(!playing);
        }}
      >
        {playing ? <Pause /> : <Play />}
      </Button>
      <Button size="xs" variant="secondary" onClick={resetBenchmark}>
        <RotateCcw />
        500 kg LEO
      </Button>
      <div className="mx-1 hidden h-4 w-px bg-border sm:block" />
      <div className="hidden min-w-0 items-center overflow-hidden md:flex">
        <Readout label="GLOW" value={glow} unit="t" />
        <Readout label="Max-Q" value={maxq} unit="kPa" />
        <Readout label="L" value={height} unit="m" />
        <Readout label="ΔV" value={dv} unit="km/s" />
      </div>
    </div>
  );
}
