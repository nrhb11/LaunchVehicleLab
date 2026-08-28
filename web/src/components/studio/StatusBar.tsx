import { useStudio } from "@/store/studio";

export function StatusBar() {
  const status = useStudio((s) => s.status);
  const vehicle = useStudio((s) => s.vehicle);
  const payloadKg = useStudio((s) => s.payloadKg);
  const altitudeKm = useStudio((s) => s.altitudeKm);
  const stage1Prop = useStudio((s) => s.stage1Prop);
  const stage2Prop = useStudio((s) => s.stage2Prop);
  const error = useStudio((s) => s.error);
  const running = useStudio((s) => s.running);

  return (
    <footer className="flex h-6 shrink-0 items-center gap-3 border-t border-border bg-raised px-2 font-mono text-micro tabular text-muted">
      <span className={error ? "text-danger" : running ? "text-warn" : "text-ok"}>
        {error ? "Error" : running ? "Busy" : "Ready"}
      </span>
      <span className="h-3 w-px bg-border" />
      <span className="min-w-0 truncate">{status}</span>
      <span className="ml-auto hidden items-center gap-3 sm:flex">
        <span>
          {payloadKg.toFixed(0)} kg · {altitudeKm.toFixed(0)} km
        </span>
        <span>
          {stage1Prop} / {stage2Prop}
        </span>
        {vehicle ? <span>{vehicle.iterations} iter</span> : null}
      </span>
    </footer>
  );
}
