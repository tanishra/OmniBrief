import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-6">
      <div className="max-w-md text-center">
        <h1 className="font-heading text-6xl font-extrabold text-ink">404</h1>
        <p className="mt-6 text-lg leading-8 text-slate">
          This page doesn&apos;t exist. If you were looking for the daily brief,
          you can find it at the homepage.
        </p>
        <Link
          href="/"
          className="mt-8 inline-flex rounded-full bg-ink px-6 py-3 text-sm font-bold text-white transition-all hover:-translate-y-0.5 hover:bg-[#262626]"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
