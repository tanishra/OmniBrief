const audience = [
  {
    label: "AI engineers",
    description:
      "People shipping models, agents, retrieval systems, and infra who need the technical essence quickly.",
  },
  {
    label: "Researchers",
    description:
      "Practitioners who want papers, repos, and implementation signals without scanning dozens of feeds every day.",
  },
  {
    label: "Technical founders",
    description:
      "Builders who need early visibility into shifts in tooling, research, and product direction before they hit the mainstream.",
  },
];

export default function AudienceSection() {
  return (
    <section id="audience" className="border-y border-black/5 bg-[#f1ede8]">
      <div className="mx-auto max-w-7xl px-6 py-24 md:px-10">
        <div className="flex flex-col gap-8 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl">
            <span className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
              Who should subscribe
            </span>
            <h2 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink md:text-5xl">
              Built for serious AI practitioners, not casual scrolling.
            </h2>
          </div>
          <p className="max-w-xl text-base leading-8 text-slate">
            If your work depends on understanding research direction, emerging
            tooling, or implementation quality, OmniBrief compresses that
            tracking workload into one dependable daily read.
          </p>
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {audience.map((item) => (
            <article
              key={item.label}
              className="rounded-[1.75rem] border border-white/60 bg-white/65 p-8 transition duration-300 hover:-translate-y-1 hover:bg-white/85 hover:shadow-editorial"
            >
              <p className="text-xs uppercase tracking-[0.18em] text-slate">Audience</p>
              <h3 className="mt-4 font-heading text-2xl font-bold text-ink">
                {item.label}
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate">{item.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
