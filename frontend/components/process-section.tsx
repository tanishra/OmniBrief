const steps = [
  {
    step: "01",
    title: "Subscribe with your email",
    body: "One field. No account maze. No setup ceremony. Just tell OmniBrief where to deliver the report.",
  },
  {
    step: "02",
    title: "Verify once",
    body: "Confirm your address from the email link. That is the only action required before delivery begins.",
  },
  {
    step: "03",
    title: "Receive a daily briefing",
    body: "Every day you get a curated technical report with the papers, repos, launches, and strategic context worth reading.",
  },
];

export default function ProcessSection() {
  return (
    <section id="process" className="mx-auto max-w-7xl px-6 py-24 md:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
          How it works
        </span>
        <h2 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink md:text-5xl">
          Simple on the surface. Deep under the hood.
        </h2>
        <p className="mt-5 text-lg leading-8 text-slate">
          Subscription should feel effortless. The complexity lives in the pipeline, not in your
          workflow.
        </p>
      </div>

      <div className="mt-16 grid gap-6 md:grid-cols-3">
        {steps.map((item) => (
          <article
            key={item.step}
            className="rounded-[1.75rem] border border-mist bg-white/70 p-8 shadow-editorial transition duration-300 hover:-translate-y-1 focus-visible:-translate-y-1 hover:shadow-[0_24px_64px_rgba(23,23,23,0.12)]"
          >
            <span className="text-xs font-semibold uppercase tracking-[0.24em] text-copper">
              Step {item.step}
            </span>
            <h3 className="mt-5 font-heading text-2xl font-bold text-ink">{item.title}</h3>
            <p className="mt-4 text-sm leading-7 text-slate">{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
