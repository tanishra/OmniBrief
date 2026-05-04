export default function MaintenanceBanner() {
  return (
    <div className="bg-accentSoft/80 border-b border-accent/10 py-3 px-6 backdrop-blur-md">
      <div className="mx-auto max-w-7xl flex items-center justify-center gap-3 text-center">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 20 20" 
          fill="currentColor" 
          className="w-5 h-5 text-accent flex-shrink-0"
        >
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
        <p className="text-sm font-medium text-accent leading-tight">
          We&apos;re currently performing technical maintenance on our scouting engine. We&apos;ll be back online with your daily briefing shortly.
        </p>
      </div>
    </div>
  );
}