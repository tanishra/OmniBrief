import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta-sans",
});

export const metadata = {
  title: "OmniBrief",
  description:
    "A premium daily AI briefing for engineers, researchers, and technical founders. Subscribe once, verify your email, and receive high-signal technical intelligence every morning.",
};

export default function RootLayout({ children }) {
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
