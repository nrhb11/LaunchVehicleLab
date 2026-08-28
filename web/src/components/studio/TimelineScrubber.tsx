import { Pause, Play, SkipBack } from "lucide-react";
import { useEffect, useMemo, useRef } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useStudio } from "@/store/studio";

const SPEEDS = [1, 5, 20, 50];

export function TimelineScrubber() {
  const traj = useStudio((s) => s.trajectory);
  const t = useStudio((s) => s.flightTime);
  const playing = useStudio((s) => s.playing);
  const speed = useStudio((s) => s.playbackSpeed);
  const setFlightTime = useStudio((s) => s.setFlightTime);
  const setPlaying = useStudio((s) => s.setPlaying);
  const setPlaybackSpeed = useStudio((s) => s.setPlaybackSpeed);

  const total = traj?.totalFlightTimeS ?? 0;
  const raf = useRef<number | null>(null);
  const last = useRef<number>(0);
  const tRef = useRef(t);
  tRef.current = t;

  useEffect(() => {
    if (!playing || !traj) return;
    last.current = performance.now();
    const tick = (now: number) => {
      const dt = ((now - last.current) / 1000) * speed;
      last.current = now;
      const next = tRef.current + dt;
      if (next >= traj.totalFlightTimeS) {
        setFlightTime(traj.totalFlightTimeS);
        setPlaying(false);
        return;
      }
      setFlightTime(next);
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [playing, speed, traj, setFlightTime, setPlaying]);

  const phases = useMemo(() => {
    if (!traj || total <= 0) return [];
    const named = (part: string) => traj.events.find((e) => e.name.toLowerCase().includes(part))?.timeS;
    const bounds = [
      { t0: 0, t1: named("pitchover") ?? 12, label: "Climb" },
      { t0: named("pitchover") ?? 12, t1: named("transonic") ?? 40, label: "Turn" },
      { t0: named("transonic") ?? 40, t1: named("meco") ?? total * 0.35, label: "Boost" },
      { t0: named("meco") ?? total * 0.35, t1: named("staging") ?? total * 0.38, label: "Sep" },
      { t0: named("staging") ?? total * 0.38, t1: named("fairing") ?? total * 0.42, label: "S2" },
      { t0: named("fairing") ?? total * 0.42, t1: total, label: "Insert" },
    ];
    return bounds.filter((p) => p.t1 > p.t0);
  }, [traj, total]);

  const ratio = total > 0 ? t / total : 0;

  return (
    <div className="flex h-10 shrink-0 items-center gap-1.5 border-t border-border bg-surface px-2 lg:h-8">
      <Button
        variant="ghost"
        size="icon-sm"
        className="size-9 lg:size-6"
        aria-label="Reset to T+0"
        onClick={() => {
          setPlaying(false);
          setFlightTime(0);
        }}
      >
        <SkipBack />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        className="size-9 lg:size-6"
        aria-label={playing ? "Pause" : "Play"}
        onClick={() => {
          if (!traj) return;
          if (t >= total) setFlightTime(0);
          setPlaying(!playing);
        }}
      >
        {playing ? <Pause /> : <Play />}
      </Button>
      <p className="w-[4.8rem] shrink-0 font-mono text-ui tabular text-fg">T+{t.toFixed(1)} s</p>
      <div
        className="relative h-5 min-w-0 flex-1 cursor-pointer border border-border bg-bg lg:h-4"
        onPointerDown={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
          setFlightTime(x * total);
        }}
        onPointerMove={(e) => {
          if (e.buttons !== 1) return;
          const rect = e.currentTarget.getBoundingClientRect();
          const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
          setFlightTime(x * total);
        }}
      >
        <div className="flex h-full overflow-hidden">
          {phases.map((p, i) => (
            <div
              key={p.label}
              className={cn(
                "flex items-center justify-center border-r border-border text-micro font-medium uppercase tracking-wide last:border-r-0",
                i % 2 === 0 ? "bg-raised text-muted" : "bg-bg text-subtle",
              )}
              style={{ width: `${((p.t1 - p.t0) / total) * 100}%` }}
            >
              <span className="hidden truncate px-1 sm:inline">{p.label}</span>
            </div>
          ))}
        </div>
        <div
          className="pointer-events-none absolute top-[-2px] h-[calc(100%+4px)] w-px bg-danger"
          style={{ left: `${ratio * 100}%` }}
        />
      </div>
      <div className="hidden border border-border bg-bg sm:flex">
        {SPEEDS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setPlaybackSpeed(s)}
            className={cn(
              "px-1.5 py-0.5 text-micro font-medium",
              speed === s ? "bg-raised text-fg" : "text-muted hover:text-fg",
            )}
          >
            {s}×
          </button>
        ))}
      </div>
    </div>
  );
}
