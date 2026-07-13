export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1 rounded-lg border border-border bg-panel px-4 py-3">
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:0ms]" />
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:160ms]" />
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:320ms]" />
      </div>
    </div>
  );
}
