import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { useStudio } from "@/store/studio";

type MenuId = "file" | "vehicle" | "sim" | "view" | "help";

interface Item {
  label: string;
  shortcut?: string;
  disabled?: boolean;
  danger?: boolean;
  onSelect?: () => void;
  separator?: boolean;
}

export function MenuBar() {
  const [open, setOpen] = useState<MenuId | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const run = useStudio((s) => s.run);
  const resetBenchmark = useStudio((s) => s.resetBenchmark);
  const setPlaying = useStudio((s) => s.setPlaying);
  const setFlightTime = useStudio((s) => s.setFlightTime);
  const playing = useStudio((s) => s.playing);
  const vehicle = useStudio((s) => s.vehicle);
  const payloadKg = useStudio((s) => s.payloadKg);
  const altitudeKm = useStudio((s) => s.altitudeKm);
  const latitudeDeg = useStudio((s) => s.latitudeDeg);
  const stage1Prop = useStudio((s) => s.stage1Prop);
  const stage2Prop = useStudio((s) => s.stage2Prop);
  const stage1DiameterM = useStudio((s) => s.stage1DiameterM);
  const stage2DiameterM = useStudio((s) => s.stage2DiameterM);

  useEffect(() => {
    const onDown = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) setOpen(null);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(null);
    };
    window.addEventListener("pointerdown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("pointerdown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  const exportJson = () => {
    const payload = {
      document: "benchmark_leo.lvl",
      inputs: { payloadKg, altitudeKm, latitudeDeg, stage1Prop, stage2Prop, stage1DiameterM, stage2DiameterM },
      vehicle: vehicle
        ? {
            glowKg: vehicle.glowKg,
            lengthM: vehicle.geometry.totalLengthM,
            deltaV: vehicle.deltaV.totalDeltaV,
            iterations: vehicle.iterations,
          }
        : null,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "benchmark_leo.lvl.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const menus: { id: MenuId; label: string; items: Item[] }[] = [
    {
      id: "file",
      label: "File",
      items: [
        { label: "Load 500 kg LEO", shortcut: "Ctrl+B", onSelect: resetBenchmark },
        { label: "Export design…", shortcut: "Ctrl+E", onSelect: exportJson },
      ],
    },
    {
      id: "vehicle",
      label: "Vehicle",
      items: [{ label: "Size & simulate", shortcut: "Ctrl+Enter", onSelect: run }],
    },
    {
      id: "sim",
      label: "Simulation",
      items: [
        {
          label: playing ? "Pause" : "Play",
          shortcut: "Space",
          onSelect: () => setPlaying(!playing),
        },
        { label: "Return to T+0", shortcut: "Home", onSelect: () => { setPlaying(false); setFlightTime(0); } },
      ],
    },
    {
      id: "view",
      label: "View",
      items: [
        { label: "Design inspector", disabled: true },
        { label: "Vehicle cutaway", disabled: true },
        { label: "Ascent traces", disabled: true },
      ],
    },
    {
      id: "help",
      label: "Help",
      items: [
        { label: "Space", shortcut: "Play / pause", disabled: true },
        { label: "Ctrl+Enter", shortcut: "Size vehicle", disabled: true },
        { label: "←  →", shortcut: "Scrub 1 s", disabled: true },
        { label: "Shift ← →", shortcut: "Scrub 10 s", disabled: true },
      ],
    },
  ];

  return (
    <div ref={root} className="flex h-6 shrink-0 items-center overflow-x-auto border-b border-border bg-surface px-1">
      {menus.map((menu) => (
        <div key={menu.id} className="relative">
          <button
            type="button"
            onClick={() => setOpen((cur) => (cur === menu.id ? null : menu.id))}
            onPointerEnter={() => {
              if (open) setOpen(menu.id);
            }}
            className={cn(
              "h-5 rounded-[var(--radius-xs)] px-2 text-ui text-fg",
              open === menu.id ? "bg-raised" : "hover:bg-raised",
            )}
          >
            {menu.label}
          </button>
          {open === menu.id ? (
            <div className="absolute left-0 top-full z-50 min-w-[220px] border border-border bg-surface py-1 shadow-none">
              {menu.items.map((item) =>
                item.separator ? (
                  <div key={item.label} className="my-1 h-px bg-border" />
                ) : (
                  <button
                    key={item.label}
                    type="button"
                    disabled={item.disabled}
                    onClick={() => {
                      item.onSelect?.();
                      setOpen(null);
                    }}
                    className={cn(
                      "flex w-full items-center justify-between gap-6 px-3 py-1 text-left text-ui",
                      item.disabled ? "text-subtle" : "text-fg hover:bg-raised",
                    )}
                  >
                    <span>{item.label}</span>
                    {item.shortcut ? <span className="font-mono text-micro text-subtle">{item.shortcut}</span> : null}
                  </button>
                ),
              )}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
