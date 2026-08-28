import { cn } from "@/lib/utils";
import { useStudio } from "@/store/studio";

export function EventsTable() {
  const traj = useStudio((s) => s.trajectory);
  const t = useStudio((s) => s.flightTime);
  const setFlightTime = useStudio((s) => s.setFlightTime);
  if (!traj) return null;

  let active = 0;
  traj.events.forEach((ev, i) => {
    if (ev.timeS <= t) active = i;
  });

  return (
    <table className="w-full text-left text-ui">
      <thead className="sticky top-0 bg-raised text-micro uppercase tracking-[0.12em] text-subtle">
        <tr className="border-b border-border">
          <th className="px-2 py-1 font-medium">Time</th>
          <th className="px-2 py-1 font-medium">Alt</th>
          <th className="hidden px-2 py-1 font-medium sm:table-cell">Vel</th>
          <th className="px-2 py-1 font-medium">Event</th>
        </tr>
      </thead>
      <tbody>
        {traj.events.map((ev, i) => (
          <tr
            key={`${ev.name}-${ev.timeS}`}
            onClick={() => setFlightTime(ev.timeS)}
            className={cn(
              "cursor-pointer border-b border-border/70",
              i === active ? "bg-raised" : "hover:bg-raised/60",
            )}
          >
            <td className="px-2 py-1 font-mono tabular text-accent">T+{ev.timeS.toFixed(1)}</td>
            <td className="px-2 py-1 font-mono tabular text-muted">{(ev.altitudeM / 1000).toFixed(1)}</td>
            <td className="hidden px-2 py-1 font-mono tabular text-muted sm:table-cell">{ev.velocity.toFixed(0)}</td>
            <td className="px-2 py-1 text-fg">{ev.name}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
