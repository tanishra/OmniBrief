const items = [
  "Finds what matters across research, code, launches, and community signals",
  "Ranks content for technical relevance instead of engagement bait",
  "Summarizes with an engineering lens so you can decide what deserves deeper time",
];

export default function ProblemSection() {
  return (
    <section id="problem" className="border-y border-black/5 bg-white/40">
      <div className="mx-auto grid max-w-7xl gap-12 px-6 py-24 md:px-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <div className="rounded-[2rem] border border-mist bg-gradient-to-br from-white to-[#ece7df] p-10 shadow-editorial">
          <div className="grid gap-6">
            <div className="rounded-2xl border border-black/5 bg-white/90 p-5">
              <p className="text-sm uppercase tracking-[0.2em] text-slate">The problem</p>
              <p className="mt-3 text-2xl font-bold leading-tight text-ink font-heading">
                AI moves too fast for manual tracking.
              </p>
            </div>
            <div className="rounded-2xl border border-black/5 bg-white/75 p-5">
              <p className="text-sm leading-7 text-slate">
                ArXiv, GitHub, blog posts, company launches, Reddit signals, Hacker News,
                newsletters, and scattered discussions all compete for your attention. Most of it is
                repetitive, shallow, or late.
              </p>
            </div>
          </div>
        </div>
        <div className="max-w-2xl">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
            Why OmniBrief exists
          </span>
          <h2 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink md:text-5xl">
            Replace scattered browsing with one precise briefing.
          </h2>
          <p className="mt-6 text-lg leading-8 text-slate">
            OmniBrief was built for the person who cares about technical signal, not algorithmic
            feeds. It turns a messy daily information hunt into one deliberate report you can
            actually use.
          </p>
          <div className="mt-8 grid gap-4">
            {items.map((item) => (
              <div
                key={item}
                className="flex items-start gap-3 rounded-2xl border border-mist bg-white/70 p-4 transition duration-300 hover:-translate-y-0.5 focus-visible:-translate-y-0.5 hover:bg-white"
              >
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-copper" />
                <p className="text-sm leading-7 text-slate">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
