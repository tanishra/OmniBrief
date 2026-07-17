"use client";

import MaintenanceBanner from "./maintenance-banner";
import { useActiveSection } from "../lib/use-active-section";

export default function HeaderSection() {
  const activeSection = useActiveSection();

  const navClass = (id: string) =>
    `focus-visible:ring-accent/40 focus-visible:outline-none focus-visible:ring-2 hover:text-ink ${
      activeSection === id ? "text-ink font-semibold" : ""
    }`;

  return (
    <header className="sticky top-0 z-40 border-b border-black/5 bg-paper/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 md:px-10">
        <a href="#top" className="font-heading text-2xl font-extrabold tracking-tightest">
          OmniBrief
        </a>
        <nav className="hidden items-center gap-8 text-sm text-slate md:flex" aria-label="Main navigation">
          <a href="#problem" className={navClass("problem")} aria-label="Why section" aria-current={activeSection === "problem" ? "true" : undefined}>Why</a>
          <a href="#process" className={navClass("process")} aria-label="How it works section" aria-current={activeSection === "process" ? "true" : undefined}>How it works</a>
          <a href="#audience" className={navClass("audience")} aria-label="Who it&apos;s for section" aria-current={activeSection === "audience" ? "true" : undefined}>Who it&apos;s for</a>
        </nav>
        <a
          href="https://github.com/tanishra/OmniBrief"
          target="_blank"
          rel="noreferrer"
          aria-label="View OmniBrief on GitHub"
          className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-black px-4 py-2 text-sm font-medium text-white hover:-translate-y-0.5 focus-visible:-translate-y-0.5 hover:bg-[#1f1f1f] hover:shadow-lg"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4 fill-current">
            <path d="M12 1.5C6.201 1.5 1.5 6.358 1.5 12.352c0 4.795 3.006 8.863 7.177 10.298.525.101.718-.234.718-.521 0-.257-.009-.938-.014-1.84-2.919.652-3.534-1.454-3.534-1.454-.477-1.255-1.165-1.589-1.165-1.589-.953-.67.072-.656.072-.656 1.054.076 1.608 1.118 1.608 1.118.937 1.664 2.458 1.183 3.057.905.095-.699.366-1.183.666-1.455-2.33-.272-4.779-1.206-4.779-5.37 0-1.187.41-2.158 1.082-2.919-.109-.273-.469-1.372.103-2.858 0 0 .882-.292 2.891 1.115A9.793 9.793 0 0 1 12 7.32a9.79 9.79 0 0 1 2.633.366c2.007-1.407 2.887-1.115 2.887-1.115.574 1.486.214 2.585.105 2.858.674.761 1.081 1.732 1.081 2.919 0 4.175-2.453 5.095-4.79 5.362.376.334.712.992.712 2 0 1.444-.013 2.609-.013 2.965 0 .289.189.627.723.52 4.167-1.437 7.169-5.503 7.169-10.296C22.5 6.358 17.799 1.5 12 1.5Z" />
          </svg>
          GitHub
        </a>
      </div>
      <MaintenanceBanner />
    </header>
  );
}
