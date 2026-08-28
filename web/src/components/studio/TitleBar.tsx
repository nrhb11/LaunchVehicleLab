export function TitleBar() {
  return (
    <header className="flex h-7 shrink-0 items-center gap-2 border-b border-border bg-surface px-2">
      <span className="grid size-4 place-items-center border border-border bg-raised">
        <svg viewBox="0 0 16 16" className="size-2.5 text-fg" aria-hidden>
          <path fill="currentColor" d="M8 1.2 9.1 5H14l-4 2.9 1.5 4.6L8 9.8 4.5 12.5 6 7.9 2 5h4.9z" />
        </svg>
      </span>
      <p className="text-ui text-fg">benchmark_leo.lvl — LaunchVehicleLab</p>
    </header>
  );
}
