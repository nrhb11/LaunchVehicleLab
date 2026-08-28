import { useEffect, useState } from "react";
import { Group, Panel, Separator as ResizeSeparator } from "react-resizable-panels";
import { TooltipProvider } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useStudio } from "@/store/studio";
import { InspectorPanel } from "./InspectorPanel";
import { MenuBar } from "./MenuBar";
import { RocketBlueprint } from "./RocketBlueprint";
import { StatusBar } from "./StatusBar";
import { TimelineScrubber } from "./TimelineScrubber";
import { TitleBar } from "./TitleBar";
import { ToolBar } from "./ToolBar";
import { TrajectoryPanel } from "./TrajectoryPanel";

const TABS = [
  { id: "design", label: "Design" },
  { id: "vehicle", label: "Vehicle" },
  { id: "flight", label: "Flight" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export function StudioApp() {
  const [tab, setTab] = useState<TabId>("design");
  const run = useStudio((s) => s.run);
  const playing = useStudio((s) => s.playing);
  const setPlaying = useStudio((s) => s.setPlaying);
  const setFlightTime = useStudio((s) => s.setFlightTime);
  const flightTime = useStudio((s) => s.flightTime);
  const traj = useStudio((s) => s.trajectory);
  const resetBenchmark = useStudio((s) => s.resetBenchmark);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const typing = target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
      if (typing) return;

      if (e.code === "Space") {
        e.preventDefault();
        if (!traj) return;
        if (flightTime >= traj.totalFlightTimeS) setFlightTime(0);
        setPlaying(!playing);
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        run();
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        resetBenchmark();
        return;
      }
      if (e.key === "Home") {
        e.preventDefault();
        setPlaying(false);
        setFlightTime(0);
        return;
      }
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        const dir = e.key === "ArrowRight" ? 1 : -1;
        const step = e.shiftKey ? 10 : 1;
        setFlightTime(flightTime + dir * step);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [flightTime, playing, resetBenchmark, run, setFlightTime, setPlaying, traj]);

  return (
    <TooltipProvider delayDuration={250}>
      <div className="app-chrome flex h-dvh min-h-0 flex-col bg-bg text-fg">
        <TitleBar />
        <MenuBar />
        <ToolBar />
        <div className="flex min-h-0 flex-1 flex-col lg:hidden">
          <div className="flex h-11 shrink-0 border-b border-border bg-surface">
            {TABS.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                className={cn(
                  "flex-1 text-ui font-medium",
                  tab === item.id ? "bg-raised text-fg" : "text-muted",
                )}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="min-h-0 flex-1 overflow-hidden">
            {tab === "design" ? <InspectorPanel /> : null}
            {tab === "vehicle" ? <RocketBlueprint /> : null}
            {tab === "flight" ? <TrajectoryPanel /> : null}
          </div>
        </div>
        <div className="hidden min-h-0 flex-1 lg:block">
          <Group orientation="horizontal" className="h-full">
            <Panel defaultSize="24%" minSize="18%" maxSize="34%" className="h-full">
              <InspectorPanel />
            </Panel>
            <ResizeSeparator className="w-px bg-border" />
            <Panel defaultSize="34%" minSize="22%" className="h-full">
              <RocketBlueprint />
            </Panel>
            <ResizeSeparator className="w-px bg-border" />
            <Panel defaultSize="42%" minSize="28%" className="h-full">
              <TrajectoryPanel />
            </Panel>
          </Group>
        </div>
        <TimelineScrubber />
        <StatusBar />
      </div>
    </TooltipProvider>
  );
}
