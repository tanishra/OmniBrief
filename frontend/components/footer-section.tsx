import ContactModal from "./contact-modal";

export default function FooterSection() {
  return (
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
  );
}
