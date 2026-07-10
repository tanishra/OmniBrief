import SubscribeForm from "./subscribe-form";

const deliverables = [
  "High-signal papers and repo releases worth your attention",
  "Technical summaries focused on architecture, tools, and implementation impact",
  "Daily synthesis of what matters for Python-first AI builders",
  "A calm, readable brief delivered to your inbox every morning",
];

export default function DeliverablesSection() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24 md:px-10">
      <div className="grid gap-12 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <div>
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
            What you receive
          </span>
          <h2 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink md:text-5xl">
            One brief that respects your attention.
          </h2>
          <p className="mt-6 text-lg leading-8 text-slate">
            The daily OmniBrief email is designed to be read quickly, trusted,
            and revisited later. It gives you enough signal to act, without
            requiring an hour of morning browsing.
          </p>
          <div className="mt-8 grid gap-4">
            {deliverables.map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-mist bg-white/65 px-5 py-4 text-sm leading-7 text-slate transition duration-300 hover:-translate-y-0.5 hover:bg-white"
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        <div
          id="final-cta"
          className="rounded-[2rem] bg-ink px-8 py-10 text-white shadow-editorial transition duration-300 hover:-translate-y-1 hover:shadow-[0_32px_90px_rgba(23,23,23,0.18)] sm:px-12 sm:py-14"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">
            Final invitation
          </p>
          <h3 className="mt-4 font-heading text-4xl font-bold tracking-tight md:text-5xl">
            Subscribe once. Verify once. Read better every day.
          </h3>
          <p className="mt-6 max-w-xl text-base leading-8 text-white/72">
            If you care about AI with an engineer&apos;s mindset, OmniBrief is
            the cleanest way to keep up without drowning in the feed.
          </p>
          <div className="mt-10">
            <SubscribeForm dark />
          </div>
        </div>
      </div>
    </section>
  );
}
