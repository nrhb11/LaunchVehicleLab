import { useMemo } from "react";
import { Area, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useStudio } from "@/store/studio";
import { DockTitle } from "./DockTitle";
import { EventsTable } from "./EventsTable";

export function TrajectoryPanel() {
  const traj = useStudio((s) => s.trajectory);
  const t = useStudio((s) => s.flightTime);
  const setFlightTime = useStudio((s) => s.setFlightTime);

  const data = useMemo(
    () =>
      (traj?.points ?? []).map((p) => ({
        t: p.timeS,
        alt: p.altitudeM / 1000,
        vel: p.velocity / 1000,
        q: p.dynamicPressurePa / 1000,
      })),
    [traj],
  );

  if (!traj) {
    return (
      <div className="flex h-full min-h-0 flex-col bg-surface">
        <DockTitle title="Ascent" />
        <div className="grid flex-1 place-items-center px-6 text-center text-ui text-muted">
          Flight traces appear after a simulation.
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col bg-surface">
      <DockTitle title="Ascent">
        <p className="font-mono text-micro tabular text-muted">
          Max-Q {(traj.maxQPa / 1000).toFixed(1)} kPa · T+{traj.maxQTimeS.toFixed(0)} s
        </p>
      </DockTitle>
      <div className="h-[42%] min-h-[160px] border-b border-border px-1 py-1">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 6, right: 8, left: 0, bottom: 0 }}
            onClick={(state) => {
              const label = state?.activeLabel;
              if (typeof label === "number") setFlightTime(label);
            }}
          >
            <CartesianGrid stroke="var(--color-border)" strokeDasharray="2 3" vertical={false} />
            <XAxis
              dataKey="t"
              tick={{ fill: "var(--color-subtle)", fontSize: 10, fontFamily: "IBM Plex Mono" }}
              tickLine={false}
              axisLine={{ stroke: "var(--color-border)" }}
              tickFormatter={(v: number) => `${v.toFixed(0)}s`}
            />
            <YAxis
              yAxisId="alt"
              tick={{ fill: "var(--color-subtle)", fontSize: 10, fontFamily: "IBM Plex Mono" }}
              tickLine={false}
              axisLine={false}
              width={32}
            />
            <YAxis
              yAxisId="q"
              orientation="right"
              tick={{ fill: "var(--color-subtle)", fontSize: 10, fontFamily: "IBM Plex Mono" }}
              tickLine={false}
              axisLine={false}
              width={28}
            />
            <Tooltip
              contentStyle={{
                background: "var(--color-raised)",
                border: "1px solid var(--color-border)",
                borderRadius: 2,
                fontSize: 11,
                fontFamily: "IBM Plex Mono, monospace",
              }}
              labelFormatter={(v) => `T+${Number(v).toFixed(1)} s`}
              formatter={(value, name) => {
                const n = Number(value);
                if (name === "alt") return [`${n.toFixed(1)} km`, "Altitude"];
                if (name === "vel") return [`${(n * 1000).toFixed(0)} m/s`, "Velocity"];
                return [`${n.toFixed(1)} kPa`, "q"];
              }}
            />
            <Area yAxisId="alt" type="monotone" dataKey="alt" fill="var(--color-accent)" fillOpacity={0.08} stroke="var(--color-accent)" strokeWidth={1.4} />
            <Line yAxisId="alt" type="monotone" dataKey="vel" stroke="var(--color-muted)" strokeWidth={1.1} dot={false} />
            <Line yAxisId="q" type="monotone" dataKey="q" stroke="var(--color-warn)" strokeWidth={1.1} dot={false} />
            <ReferenceLine yAxisId="alt" x={t} stroke="var(--color-danger)" strokeWidth={1} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <ScrollArea className="min-h-0 flex-1">
        <EventsTable />
      </ScrollArea>
    </div>
  );
}
