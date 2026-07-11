import HeaderSection from "../components/header-section";
import HeroSection from "../components/hero-section";
import ProblemSection from "../components/problem-section";
import ProcessSection from "../components/process-section";
import AudienceSection from "../components/audience-section";
import DeliverablesSection from "../components/deliverables-section";
import FooterSection from "../components/footer-section";

export default function HomePage() {
  return (
    <main className="overflow-hidden">
      <HeaderSection />
      <HeroSection />
      <ProblemSection />
      <ProcessSection />
      <AudienceSection />
      <DeliverablesSection />
      <FooterSection />
    </main>
  );
}
