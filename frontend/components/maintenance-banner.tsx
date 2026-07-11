export default function MaintenanceBanner() {
  return (
    <div className="relative z-50 w-full bg-accentSoft border-b border-accent/20 py-2.5 px-6">
      <div className="mx-auto max-w-7xl flex items-center justify-center gap-3 text-center">
        <div className="flex-shrink-0">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 20 20" 
            fill="currentColor" 
            className="w-5 h-5 text-accent"
          >
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        </div>
        <p className="text-sm font-semibold text-accent leading-tight">
          System Update: We&apos;re currently performing technical maintenance on our scouting engine. We&apos;ll be back with your daily briefing shortly.
        </p>
      </div>
    </div>
  );
}
