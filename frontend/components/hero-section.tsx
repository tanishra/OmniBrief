import SubscribeForm from "./subscribe-form";

export default function HeroSection() {
  return (
    <section id="top" className="mx-auto max-w-7xl px-6 pb-24 pt-20 md:px-10 md:pb-32 md:pt-28">
      <div className="grid gap-14 lg:grid-cols-[minmax(0,1.2fr)_28rem] lg:items-end">
        <div className="max-w-4xl">
          <span className="mb-8 inline-flex rounded-full border border-accent/15 bg-accentSoft/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-accent">
            Daily AI briefing for technical minds
          </span>
          <h1 className="max-w-4xl font-heading text-5xl font-extrabold leading-[0.95] tracking-tightest text-ink md:text-7xl">
            High-signal AI intelligence, distilled into one calm daily report.
          </h1>
          <p className="mt-8 max-w-2xl text-lg leading-8 text-slate md:text-xl">
            OmniBrief scans the global AI landscape, filters the noise, and delivers a single
            technical briefing covering the papers, repos, launches, and shifts that serious
            builders actually need to know.
          </p>
          <div id="subscribe" className="mt-10 max-w-xl">
            <SubscribeForm />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-slate">
            <span>One email. Daily.</span>
            <span className="h-1 w-1 rounded-full bg-slate/70" />
            <span>Simple email verification.</span>
            <span className="h-1 w-1 rounded-full bg-slate/70" />
            <span>No dashboards. No clutter.</span>
          </div>
        </div>

        <div className="rounded-[2rem] border border-mist/80 bg-white/75 p-7 shadow-editorial transition duration-300 hover:-translate-y-1 focus-visible:-translate-y-1 hover:shadow-[0_28px_80px_rgba(23,23,23,0.12)]">
          <div className="flex items-center justify-between border-b border-mist pb-4">
            <span className="font-heading text-lg font-bold">Today&apos;s Brief</span>
            <span className="rounded-full bg-accentSoft px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-accent">
              Sample
            </span>
          </div>
          <div className="space-y-5 pt-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
                Executive synthesis
              </p>
              <p className="mt-2 text-sm leading-7 text-slate">
                Agentic infra is maturing from toy orchestration to reliable workflows, while
                research emphasis keeps shifting toward efficiency, context management, and
                practical deployment.
              </p>
            </div>
            <div className="grid gap-4 border-t border-mist pt-5">
              <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 focus-visible:-translate-y-1 hover:bg-white">
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Research</p>
                <p className="mt-2 font-heading text-lg font-bold">
                  Frontier paper with linked implementation
                </p>
              </div>
              <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 focus-visible:-translate-y-1 hover:bg-white">
                <p className="text-xs uppercase tracking-[0.18em] text-slate">GitHub</p>
                <p className="mt-2 font-heading text-lg font-bold">
                  High-velocity Python repo with real technical leverage
                </p>
              </div>
              <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 focus-visible:-translate-y-1 hover:bg-white">
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Signal</p>
                <p className="mt-2 font-heading text-lg font-bold">
                  One crisp strategic read on what the day actually means
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
