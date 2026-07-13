export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-paper">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-mist border-t-ink" />
        <p className="text-sm text-slate">Loading OmniBrief...</p>
      </div>
    </div>
  );
}
