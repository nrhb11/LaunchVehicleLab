import type { CoupledVehicleResult, TrajectoryResult } from "@/lib/lvlab/types";
import { useStudio } from "@/store/studio";
import { DockTitle } from "./DockTitle";

function n(v: number): number {
  return Math.round(v * 100) / 100;
}

function fuelFill(name: string): string {
  if (name.includes("Hydrolox") || name.includes("LH2")) return "var(--color-lh2)";
  if (name.includes("Methalox") || name.includes("CH4")) return "var(--color-ch4)";
  return "var(--color-rp1)";
}

function eventTime(traj: TrajectoryResult | null, match: string, fallback: number): number {
  const hit = traj?.events.find((e) => e.name.toLowerCase().includes(match));
  return hit?.timeS ?? fallback;
}

export function RocketBlueprint() {
  const vehicle = useStudio((s) => s.vehicle);
  const traj = useStudio((s) => s.trajectory);
  const t = useStudio((s) => s.flightTime);

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg">
      <DockTitle title="Vehicle">
        {vehicle ? (
          <p className="font-mono text-micro tabular text-muted">
            {vehicle.geometry.totalLengthM.toFixed(2)} m · L/D {vehicle.geometry.finenessRatio.toFixed(1)}
          </p>
        ) : null}
      </DockTitle>
      {!vehicle ? (
        <div className="grid min-h-[280px] flex-1 place-items-center bg-bg px-6 text-center">
          <p className="max-w-xs text-ui text-muted">Size a vehicle to generate the stack cutaway.</p>
        </div>
      ) : (
        <div className="min-h-0 flex-1">
          <BlueprintSvg vehicle={vehicle} traj={traj} timeS={t} />
        </div>
      )}
    </div>
  );
}

function BlueprintSvg({
  vehicle,
  traj,
  timeS,
}: {
  vehicle: CoupledVehicleResult;
  traj: TrajectoryResult | null;
  timeS: number;
}) {
  const geom = vehicle.geometry;
  const tMeco = eventTime(traj, "meco", 174);
  const tStage = eventTime(traj, "staging", 176);
  const tFairing = eventTime(traj, "fairing", 186);
  const tSeco = eventTime(traj, "seco", traj?.totalFlightTimeS ?? 500);

  const s1Fire = timeS > 0 && timeS < tMeco;
  const staged = timeS >= tStage;
  const s2Fire = timeS >= tStage && timeS < tSeco;
  const fairingOpen = timeS >= tFairing;

  const W = 420;
  const H = 760;
  const padY = 48;
  const scale = (H - padY * 2 - 40) / geom.totalLengthM;
  const m = (meters: number) => meters * scale;
  const dia = (d: number) => Math.max(36, d * scale * 2.15);
  const cx = 168;

  const fairing = geom.fairing;
  const s2 = vehicle.stage2;
  const s1 = vehicle.stage1;

  let y = padY;
  const fY = y;
  const fH = m(fairing.totalLengthM);
  const fNose = m(fairing.noseConeLengthM);
  const fD = dia(fairing.diameterM);
  y += fH;

  const ox2Y = y;
  const ox2H = m(s2.geometry.oxidizerTank.totalLengthM);
  const s2D = dia(s2.geometry.diameterM);
  y += ox2H;
  const fuel2Y = y;
  const fuel2H = m(s2.geometry.fuelTank.totalLengthM);
  y += fuel2H;
  const skirt2Y = y;
  const skirt2H = Math.max(18, m(s2.geometry.skirtLengthM));
  y += skirt2H;

  const interH = Math.max(14, m(geom.interstageLengthM));
  const interY = y;
  y += staged ? 16 : interH;

  const ox1Y = y;
  const ox1H = m(s1.geometry.oxidizerTank.totalLengthM);
  const s1D = dia(s1.geometry.diameterM);
  y += ox1H;
  const fuel1Y = y;
  const fuel1H = m(s1.geometry.fuelTank.totalLengthM);
  y += fuel1H;
  const skirt1Y = y;
  const skirt1H = Math.max(22, m(s1.geometry.skirtLengthM));
  const stackBottom = skirt1Y + skirt1H;

  return (
    <div className="relative h-full min-h-[320px] bg-bg">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="absolute inset-0 h-full w-full"
        role="img"
        aria-label="Launch vehicle cutaway blueprint"
      >
        <rect width={W} height={H} fill="var(--color-bg)" />
        {Array.from({ length: 24 }, (_, i) => (
          <line
            key={`v-${i}`}
            x1={(i * W) / 24}
            y1={0}
            x2={(i * W) / 24}
            y2={H}
            stroke="var(--color-border)"
            strokeWidth="0.6"
            opacity="0.45"
          />
        ))}
        {Array.from({ length: 32 }, (_, i) => (
          <line
            key={`h-${i}`}
            x1={0}
            y1={(i * H) / 32}
            x2={W}
            y2={(i * H) / 32}
            stroke="var(--color-border)"
            strokeWidth="0.6"
            opacity="0.45"
          />
        ))}
        <line
          x1={cx}
          y1={padY - 16}
          x2={cx}
          y2={n(stackBottom + 10)}
          stroke="var(--color-subtle)"
          strokeWidth="0.8"
          strokeDasharray="4 5"
          opacity="0.7"
        />

        {!fairingOpen ? (
          <Fairing cx={n(cx)} y={n(fY)} d={n(fD)} len={n(fH)} nose={n(fNose)} />
        ) : (
          <Satellite cx={n(cx)} y={n(fY)} d={n(fD)} len={n(fH)} />
        )}

        <Tank
          cx={n(cx)}
          y={n(ox2Y)}
          d={n(s2D)}
          len={n(ox2H)}
          fill="var(--color-lox)"
          label="S2 LOX"
          mass={s2.oxidizerMassKg}
        />
        <Tank
          cx={n(cx)}
          y={n(fuel2Y)}
          d={n(s2D)}
          len={n(fuel2H)}
          fill={fuelFill(s2.propellant.name)}
          label="S2 FUEL"
          mass={s2.fuelMassKg}
        />
        <EngineBay cx={n(cx)} y={n(skirt2Y)} d={n(s2D)} h={n(skirt2H)} bells={1} />
        {s2Fire ? <Plume cx={n(cx)} y={n(skirt2Y + skirt2H)} w={n(s2D * 0.5)} h={42} /> : null}

        {!staged ? (
          <rect
            x={n(cx - s1D / 2)}
            y={n(interY)}
            width={n(s1D)}
            height={n(interH)}
            fill="var(--color-bg)"
            stroke="var(--color-border)"
            strokeWidth="1.2"
          />
        ) : (
          <line
            x1={n(cx - 40)}
            y1={n(interY + 6)}
            x2={n(cx + 40)}
            y2={n(interY + 6)}
            stroke="var(--color-danger)"
            strokeWidth="1.4"
            strokeDasharray="4 3"
          />
        )}

        <g opacity={staged ? 0.28 : 1}>
          <Tank
            cx={n(cx)}
            y={n(ox1Y)}
            d={n(s1D)}
            len={n(ox1H)}
            fill="var(--color-lox)"
            label="S1 LOX"
            mass={s1.oxidizerMassKg}
          />
          <Tank
            cx={n(cx)}
            y={n(fuel1Y)}
            d={n(s1D)}
            len={n(fuel1H)}
            fill={fuelFill(s1.propellant.name)}
            label="S1 FUEL"
            mass={s1.fuelMassKg}
          />
          <EngineBay cx={n(cx)} y={n(skirt1Y)} d={n(s1D)} h={n(skirt1H)} bells={3} />
        </g>
        {s1Fire ? <Plume cx={n(cx)} y={n(skirt1Y + skirt1H)} w={n(s1D * 0.72)} h={56} /> : null}

        <line x1={36} y1={padY} x2={36} y2={n(stackBottom)} stroke="var(--color-muted)" strokeWidth="1" />
        <line x1={30} y1={padY} x2={42} y2={padY} stroke="var(--color-muted)" strokeWidth="1" />
        <line x1={30} y1={n(stackBottom)} x2={42} y2={n(stackBottom)} stroke="var(--color-muted)" strokeWidth="1" />
        <text
          x={22}
          y={n((padY + stackBottom) / 2)}
          fill="var(--color-muted)"
          fontSize="11"
          fontFamily="IBM Plex Mono, monospace"
          textAnchor="middle"
          transform={`rotate(-90 22 ${n((padY + stackBottom) / 2)})`}
        >
          {geom.totalLengthM.toFixed(1)} m · L/D {geom.finenessRatio.toFixed(1)}
        </text>

        <Callout
          x={n(cx + fD / 2 + 14)}
          y={n(fY + fH * 0.42)}
          title={fairingOpen ? "Payload" : "Fairing"}
          sub={`${fairing.diameterM.toFixed(1)} m · ${vehicle.mission.payloadMassKg.toFixed(0)} kg`}
        />
        <Callout
          x={n(cx + s2D / 2 + 14)}
          y={n(ox2Y + (ox2H + fuel2H) * 0.45)}
          title="Stage 2"
          sub={`${s2.propellant.key} · ${(s2.sizing.deltaV / 1000).toFixed(2)} km/s`}
        />
        <Callout
          x={n(cx + s1D / 2 + 14)}
          y={n(ox1Y + (ox1H + fuel1H) * 0.4)}
          title="Stage 1"
          sub={`${s1.propellant.key} · ${(s1.sizing.deltaV / 1000).toFixed(2)} km/s`}
        />
      </svg>
    </div>
  );
}

function Tank({
  cx,
  y,
  d,
  len,
  fill,
  label,
  mass,
}: {
  cx: number;
  y: number;
  d: number;
  len: number;
  fill: string;
  label: string;
  mass: number;
}) {
  const r = 3;
  return (
    <g>
      <rect x={cx - d / 2} y={y} width={d} height={len} rx={r} fill="var(--color-raised)" stroke={fill} strokeWidth="1.6" />
      <rect
        x={cx - d / 2 + 4}
        y={y + 6}
        width={d * 0.5}
        height={Math.max(8, len - 12)}
        rx={2}
        fill={fill}
        opacity="0.42"
      />
      <text
        x={cx}
        y={y + len / 2 - 4}
        textAnchor="middle"
        fill="var(--color-fg)"
        fontSize="11"
        fontFamily="IBM Plex Sans, sans-serif"
        fontWeight="500"
      >
        {label}
      </text>
      <text
        x={cx}
        y={y + len / 2 + 12}
        textAnchor="middle"
        fill="var(--color-muted)"
        fontSize="10"
        fontFamily="IBM Plex Mono, monospace"
      >
        {mass.toFixed(0)} kg
      </text>
    </g>
  );
}

function Fairing({ cx, y, d, len, nose }: { cx: number; y: number; d: number; len: number; nose: number }) {
  const r = d / 2;
  const body = len - nose;
  const path = `M ${cx} ${y} Q ${cx - r * 0.72} ${y + nose * 0.58} ${cx - r} ${y + nose} L ${cx - r} ${y + nose + body} L ${cx + r} ${y + nose + body} L ${cx + r} ${y + nose} Q ${cx + r * 0.72} ${y + nose * 0.58} ${cx} ${y} Z`;
  return <path d={path} fill="var(--color-raised)" stroke="var(--color-fairing)" strokeWidth="1.6" />;
}

function Satellite({ cx, y, d, len }: { cx: number; y: number; d: number; len: number }) {
  const w = d * 0.42;
  const h = len * 0.48;
  return (
    <g>
      <rect
        x={cx - w / 2}
        y={y + len * 0.18}
        width={w}
        height={h}
        rx="2"
        fill="var(--color-surface)"
        stroke="var(--color-accent)"
        strokeWidth="1.4"
      />
      <rect
        x={cx - w * 1.35}
        y={y + len * 0.3}
        width={w * 0.72}
        height={h * 0.38}
        fill="var(--color-raised)"
        stroke="var(--color-lox)"
        strokeWidth="1.1"
      />
      <rect
        x={cx + w * 0.63}
        y={y + len * 0.3}
        width={w * 0.72}
        height={h * 0.38}
        fill="var(--color-raised)"
        stroke="var(--color-lox)"
        strokeWidth="1.1"
      />
    </g>
  );
}

function EngineBay({ cx, y, d, h, bells }: { cx: number; y: number; d: number; h: number; bells: number }) {
  const items = Array.from({ length: bells }, (_, i) => i);
  const spacing = d / (bells + 1);
  return (
    <g>
      <rect x={cx - d / 2} y={y} width={d} height={h} fill="var(--color-bg)" stroke="var(--color-border)" strokeWidth="1.2" />
      {items.map((i) => {
        const bx = cx - d / 2 + (i + 1) * spacing;
        const bw = spacing * 0.4;
        return (
          <polygon
            key={i}
            points={`${n(bx - bw * 0.35)},${n(y)} ${n(bx + bw * 0.35)},${n(y)} ${n(bx + bw)},${n(y + h)} ${n(bx - bw)},${n(y + h)}`}
            fill="var(--color-raised)"
            stroke="var(--color-subtle)"
            strokeWidth="1"
          />
        );
      })}
    </g>
  );
}

function Plume({ cx, y, w, h }: { cx: number; y: number; w: number; h: number }) {
  return (
    <g>
      <path
        d={`M ${cx - w / 2} ${y} Q ${cx - w * 0.75} ${y + h * 0.55} ${cx} ${y + h} Q ${cx + w * 0.75} ${y + h * 0.55} ${cx + w / 2} ${y} Z`}
        fill="var(--color-accent)"
        opacity="0.4"
      />
      <path
        d={`M ${cx - w * 0.16} ${y} Q ${cx} ${y + h * 0.72} ${cx} ${y + h * 0.88} Q ${cx} ${y + h * 0.72} ${cx + w * 0.16} ${y} Z`}
        fill="var(--color-fg)"
        opacity="0.55"
      />
    </g>
  );
}

function Callout({ x, y, title, sub }: { x: number; y: number; title: string; sub: string }) {
  return (
    <g>
      <circle cx={x - 8} cy={y} r="2.4" fill="var(--color-accent)" />
      <text x={x} y={y - 2} fill="var(--color-fg)" fontSize="12" fontFamily="IBM Plex Sans, sans-serif" fontWeight="500">
        {title}
      </text>
      <text x={x} y={y + 13} fill="var(--color-muted)" fontSize="10" fontFamily="IBM Plex Mono, monospace">
        {sub}
      </text>
    </g>
  );
}
