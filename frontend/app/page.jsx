import SubscribeForm from "../components/subscribe-form";
import ContactModal from "../components/contact-modal";
import MaintenanceBanner from "../components/maintenance-banner";

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

const deliverables = [
  "High-signal papers and repo releases worth your attention",
  "Technical summaries focused on architecture, tools, and implementation impact",
  "Daily synthesis of what matters for Python-first AI builders",
  "A calm, readable brief delivered to your inbox every morning",
];

export default function HomePage() {
  return (
    <main className="overflow-hidden">
      <header className="sticky top-0 z-40 border-b border-black/5 bg-paper/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 md:px-10">
          <a href="#top" className="font-heading text-2xl font-extrabold tracking-tightest">
            OmniBrief
          </a>
          <nav className="hidden items-center gap-8 text-sm text-slate md:flex">
            <a href="#problem" className="hover:text-ink">
              Why
            </a>
            <a href="#process" className="hover:text-ink">
              How it works
            </a>
            <a href="#audience" className="hover:text-ink">
              Who it&apos;s for
            </a>
          </nav>
          <a
            href="https://github.com/tanishra/OmniBrief"
            target="_blank"
            rel="noreferrer"
            aria-label="View OmniBrief on GitHub"
            className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-black px-4 py-2 text-sm font-medium text-white hover:-translate-y-0.5 hover:bg-[#1f1f1f] hover:shadow-lg"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              className="h-4 w-4 fill-current"
            >
              <path d="M12 1.5C6.201 1.5 1.5 6.358 1.5 12.352c0 4.795 3.006 8.863 7.177 10.298.525.101.718-.234.718-.521 0-.257-.009-.938-.014-1.84-2.919.652-3.534-1.454-3.534-1.454-.477-1.255-1.165-1.589-1.165-1.589-.953-.67.072-.656.072-.656 1.054.076 1.608 1.118 1.608 1.118.937 1.664 2.458 1.183 3.057.905.095-.699.366-1.183.666-1.455-2.33-.272-4.779-1.206-4.779-5.37 0-1.187.41-2.158 1.082-2.919-.109-.273-.469-1.372.103-2.858 0 0 .882-.292 2.891 1.115A9.793 9.793 0 0 1 12 7.32a9.79 9.79 0 0 1 2.633.366c2.007-1.407 2.887-1.115 2.887-1.115.574 1.486.214 2.585.105 2.858.674.761 1.081 1.732 1.081 2.919 0 4.175-2.453 5.095-4.79 5.362.376.334.712.992.712 2 0 1.444-.013 2.609-.013 2.965 0 .289.189.627.723.52 4.167-1.437 7.169-5.503 7.169-10.296C22.5 6.358 17.799 1.5 12 1.5Z" />
            </svg>
            GitHub
          </a>
        </div>
        <MaintenanceBanner />
      </header>


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
              OmniBrief scans the global AI landscape, filters the noise, and
              delivers a single technical briefing covering the papers, repos,
              launches, and shifts that serious builders actually need to know.
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

          <div className="rounded-[2rem] border border-mist/80 bg-white/75 p-7 shadow-editorial transition duration-300 hover:-translate-y-1 hover:shadow-[0_28px_80px_rgba(23,23,23,0.12)]">
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
                  Agentic infra is maturing from toy orchestration to reliable
                  workflows, while research emphasis keeps shifting toward
                  efficiency, context management, and practical deployment.
                </p>
              </div>
              <div className="grid gap-4 border-t border-mist pt-5">
                <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 hover:bg-white">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">
                    Research
                  </p>
                  <p className="mt-2 font-heading text-lg font-bold">
                    Frontier paper with linked implementation
                  </p>
                </div>
                <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 hover:bg-white">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">
                    GitHub
                  </p>
                  <p className="mt-2 font-heading text-lg font-bold">
                    High-velocity Python repo with real technical leverage
                  </p>
                </div>
                <div className="rounded-2xl bg-paper p-4 transition duration-300 hover:-translate-y-1 hover:bg-white">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">
                    Signal
                  </p>
                  <p className="mt-2 font-heading text-lg font-bold">
                    One crisp strategic read on what the day actually means
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="problem" className="border-y border-black/5 bg-white/40">
        <div className="mx-auto grid max-w-7xl gap-12 px-6 py-24 md:px-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <div className="rounded-[2rem] border border-mist bg-gradient-to-br from-white to-[#ece7df] p-10 shadow-editorial">
            <div className="grid gap-6">
              <div className="rounded-2xl border border-black/5 bg-white/90 p-5">
                <p className="text-sm uppercase tracking-[0.2em] text-slate">
                  The problem
                </p>
                <p className="mt-3 text-2xl font-bold leading-tight text-ink font-heading">
                  AI moves too fast for manual tracking.
                </p>
              </div>
              <div className="rounded-2xl border border-black/5 bg-white/75 p-5">
                <p className="text-sm leading-7 text-slate">
                  ArXiv, GitHub, blog posts, company launches, Reddit signals,
                  Hacker News, newsletters, and scattered discussions all compete
                  for your attention. Most of it is repetitive, shallow, or late.
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
              OmniBrief was built for the person who cares about technical
              signal, not algorithmic feeds. It turns a messy daily information
              hunt into one deliberate report you can actually use.
            </p>
            <div className="mt-8 grid gap-4">
              {[
                "Finds what matters across research, code, launches, and community signals",
                "Ranks content for technical relevance instead of engagement bait",
                "Summarizes with an engineering lens so you can decide what deserves deeper time",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-start gap-3 rounded-2xl border border-mist bg-white/70 p-4 transition duration-300 hover:-translate-y-0.5 hover:bg-white"
                >
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-copper" />
                  <p className="text-sm leading-7 text-slate">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="process" className="mx-auto max-w-7xl px-6 py-24 md:px-10">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
            How it works
          </span>
          <h2 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink md:text-5xl">
            Simple on the surface. Deep under the hood.
          </h2>
          <p className="mt-5 text-lg leading-8 text-slate">
            Subscription should feel effortless. The complexity lives in the
            pipeline, not in your workflow.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {[
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
          ].map((item) => (
            <article
              key={item.step}
              className="rounded-[1.75rem] border border-mist bg-white/70 p-8 shadow-editorial transition duration-300 hover:-translate-y-1 hover:shadow-[0_24px_64px_rgba(23,23,23,0.12)]"
            >
              <span className="text-xs font-semibold uppercase tracking-[0.24em] text-copper">
                Step {item.step}
              </span>
              <h3 className="mt-5 font-heading text-2xl font-bold text-ink">
                {item.title}
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate">{item.body}</p>
            </article>
          ))}
        </div>
      </section>

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
                <p className="text-xs uppercase tracking-[0.18em] text-slate">
                  Audience
                </p>
                <h3 className="mt-4 font-heading text-2xl font-bold text-ink">
                  {item.label}
                </h3>
                <p className="mt-4 text-sm leading-7 text-slate">{item.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

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

      <footer className="border-t border-black/5 px-6 py-10 md:px-10">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-heading text-xl font-bold">OmniBrief</p>
            <p className="mt-2 text-sm text-slate">
              A daily AI briefing for engineers, researchers, and technical builders.
            </p>
          </div>
          <div className="flex flex-wrap gap-6 text-sm text-slate">
            <ContactModal />
          </div>
        </div>
      </footer>
    </main>
  );
}
