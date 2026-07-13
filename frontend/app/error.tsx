"use client";

import { useEffect } from "react";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error("Page error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-6">
      <div className="max-w-md text-center">
        <h1 className="font-heading text-6xl font-extrabold text-ink">500</h1>
        <p className="mt-6 text-lg leading-8 text-slate">
          Something went wrong on our end. The team has been notified.
        </p>
        <button
          onClick={() => reset()}
          className="mt-8 inline-flex rounded-full bg-ink px-6 py-3 text-sm font-bold text-white transition-all hover:-translate-y-0.5 hover:bg-[#262626]"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
