import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { PropellantName } from "@/lib/lvlab/types";
import { useStudio } from "@/store/studio";
import { DockTitle } from "./DockTitle";
import { TelemetryHud } from "./TelemetryHud";

const PROP_OPTIONS: { id: PropellantName; label: string }[] = [
  { id: "KEROLOX", label: "RP-1" },
  { id: "METHALOX", label: "CH4" },
  { id: "HYDROLOX", label: "LH2" },
];

function Field({
  label,
  value,
  unit,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  unit: string;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-x-2 gap-y-1 px-2 py-1.5">
      <span className="text-ui text-muted">{label}</span>
      <span className="flex items-center gap-1 font-mono text-ui tabular text-fg">
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="h-6 w-16 border border-border bg-bg px-1.5 text-right text-ui text-fg outline-none focus:border-accent"
        />
        <span className="w-6 text-subtle">{unit}</span>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="col-span-2 h-1 w-full cursor-pointer appearance-none bg-bg accent-accent"
      />
    </div>
  );
}

function Segmented({
  label,
  value,
  onChange,
}: {
  label: string;
  value: PropellantName;
  onChange: (v: PropellantName) => void;
}) {
  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-2 px-2 py-1.5">
      <span className="text-ui text-muted">{label}</span>
      <div className="flex border border-border bg-bg">
        {PROP_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            type="button"
            onClick={() => onChange(opt.id)}
            className={cn(
              "px-2 py-0.5 text-micro font-medium",
              value === opt.id ? "bg-raised text-fg" : "text-muted hover:text-fg",
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function InspectorPanel() {
  const payloadKg = useStudio((s) => s.payloadKg);
  const altitudeKm = useStudio((s) => s.altitudeKm);
  const latitudeDeg = useStudio((s) => s.latitudeDeg);
  const stage1Prop = useStudio((s) => s.stage1Prop);
  const stage2Prop = useStudio((s) => s.stage2Prop);
  const stage1DiameterM = useStudio((s) => s.stage1DiameterM);
  const stage2DiameterM = useStudio((s) => s.stage2DiameterM);
  const setField = useStudio((s) => s.setField);
  const setStage1Prop = useStudio((s) => s.setStage1Prop);
  const setStage2Prop = useStudio((s) => s.setStage2Prop);
  const error = useStudio((s) => s.error);
  const vehicle = useStudio((s) => s.vehicle);

  return (
    <div className="flex h-full min-h-0 flex-col bg-surface">
      <DockTitle title="Design" />
      <ScrollArea className="flex-1">
        <div className="flex flex-col pb-6">
          <SectionLabel>Mission</SectionLabel>
          <Field label="Payload" value={payloadKg} unit="kg" min={50} max={5000} step={50} onChange={(v) => setField("payloadKg", v)} />
          <Field label="Orbit" value={altitudeKm} unit="km" min={200} max={1200} step={25} onChange={(v) => setField("altitudeKm", v)} />
          <Field label="Latitude" value={latitudeDeg} unit="°" min={0} max={70} step={0.5} onChange={(v) => setField("latitudeDeg", v)} />

          <SectionLabel>Propulsion</SectionLabel>
          <Segmented label="Stage 1" value={stage1Prop} onChange={setStage1Prop} />
          <Segmented label="Stage 2" value={stage2Prop} onChange={setStage2Prop} />
          <Field
            label="S1 diameter"
            value={Number(stage1DiameterM.toFixed(1))}
            unit="m"
            min={0.8}
            max={4}
            step={0.1}
            onChange={(v) => setField("stage1DiameterM", v)}
          />
          <Field
            label="S2 diameter"
            value={Number(stage2DiameterM.toFixed(1))}
            unit="m"
            min={0.8}
            max={4}
            step={0.1}
            onChange={(v) => setField("stage2DiameterM", v)}
          />

          {error ? <p className="px-2 py-2 text-ui text-danger">{error}</p> : null}

          {vehicle ? (
            <>
              <SectionLabel>ΔV budget</SectionLabel>
              <BudgetRow label="Orbital velocity" value={vehicle.deltaV.orbitalVelocity} />
              <BudgetRow label="Earth rotation" value={-vehicle.deltaV.earthRotationBoost} />
              <BudgetRow
                label="Gravity + drag + steer"
                value={vehicle.deltaV.gravityLoss + vehicle.deltaV.dragLoss + vehicle.deltaV.steeringLoss}
              />
              <BudgetRow label="Margin" value={vehicle.deltaV.margin} />
              <BudgetRow label="Total" value={vehicle.deltaV.totalDeltaV} strong />
            </>
          ) : null}

          <TelemetryHud />
        </div>
      </ScrollArea>
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div className="border-y border-border bg-raised px-2 py-1 text-micro font-medium uppercase tracking-[0.14em] text-subtle">
      {children}
    </div>
  );
}

function BudgetRow({ label, value, strong }: { label: string; value: number; strong?: boolean }) {
  return (
    <div className={cn("flex items-baseline justify-between px-2 py-1 text-ui", strong ? "text-fg" : "text-muted")}>
      <span>{label}</span>
      <span className="font-mono tabular">
        {value >= 0 ? "" : "−"}
        {Math.abs(value).toFixed(0)}
        <span className="ml-1 text-subtle">m/s</span>
      </span>
    </div>
  );
}
