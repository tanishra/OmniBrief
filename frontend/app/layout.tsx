import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta-sans",
  display: "swap",
});

export const metadata = {
  metadataBase: new URL("https://omni-brief.vercel.app"),
  title: "OmniBrief — Daily AI Briefing for Technical Minds",
  description:
    "A premium daily AI briefing for engineers, researchers, and technical founders. Subscribe once, verify your email, and receive high-signal technical intelligence every morning.",
  icons: { icon: "/favicon.svg" },
  openGraph: {
    title: "OmniBrief — Daily AI Briefing",
    description:
      "High-signal AI intelligence, distilled into one calm daily report.",
    url: "https://omni-brief.vercel.app",
    siteName: "OmniBrief",
    images: [{ url: "/og-image.svg", width: 1200, height: 630 }],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OmniBrief — Daily AI Briefing",
    description:
      "High-signal AI intelligence, distilled into one calm daily report.",
    images: ["/og-image.svg"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth bg-paper">
      <body
        className={`${inter.variable} ${plusJakartaSans.variable} bg-paper font-body text-ink antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
