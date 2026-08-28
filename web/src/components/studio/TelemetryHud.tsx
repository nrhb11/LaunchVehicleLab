import { nearestPoint } from "@/lib/lvlab/physics";
import { useStudio } from "@/store/studio";

function Row({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="flex items-baseline justify-between px-2 py-1 text-ui">
      <span className="text-muted">{label}</span>
      <span className="font-mono tabular text-fg">
        {value}
        <span className="ml-1 text-subtle">{unit}</span>
      </span>
    </div>
  );
}

export function TelemetryHud() {
  const traj = useStudio((s) => s.trajectory);
  const time = useStudio((s) => s.flightTime);
  const point = traj ? nearestPoint(traj.points, time) : null;
  if (!point || !traj) return null;

  return (
    <section>
      <div className="border-y border-border bg-raised px-2 py-1 text-micro font-medium uppercase tracking-[0.14em] text-subtle">
        Telemetry
      </div>
      <Row label="Altitude" value={(point.altitudeM / 1000).toFixed(1)} unit="km" />
      <Row label="Velocity" value={point.velocity.toFixed(0)} unit="m/s" />
      <Row label="Dynamic pressure" value={(point.dynamicPressurePa / 1000).toFixed(1)} unit="kPa" />
      <Row label="Axial load" value={point.accelerationG.toFixed(2)} unit="g" />
    </section>
  );
}
