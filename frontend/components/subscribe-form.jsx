"use client";

import { useId, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://omni.tanish.website";

export default function SubscribeForm({ compact = false, dark = false }) {
  const inputId = useId();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/subscribe`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Subscription request failed.");
      }

      const data = await response.json();
      setStatus("success");
      setMessage(data.message);
      setEmail("");
    } catch (error) {
      setStatus("error");
      setMessage("Something went wrong. Please try again in a minute.");
    }
  }

  const wrapperClass = dark
    ? "border border-white/15 bg-white/10"
    : "border border-mist/80 bg-white/75 shadow-editorial";

  const inputClass = dark
    ? "text-white placeholder:text-white/45"
    : "text-ink placeholder:text-slate/70";

  const buttonClass = dark
    ? "bg-paper text-ink hover:-translate-y-0.5 hover:bg-white hover:shadow-lg"
    : "bg-ink text-white hover:-translate-y-0.5 hover:bg-[#262626] hover:shadow-lg";

  const feedbackClass =
    status === "success"
      ? dark
        ? "border border-emerald-300/25 bg-emerald-300/10 text-emerald-100"
        : "border border-emerald-200 bg-emerald-50 text-emerald-900"
      : status === "error"
        ? dark
          ? "border border-red-300/25 bg-red-300/10 text-red-100"
          : "border border-red-200 bg-red-50 text-red-900"
        : dark
          ? "text-white/70"
          : "text-slate";

  return (
    <div className="w-full">
      <label
        htmlFor={inputId}
        className={`mb-3 block text-xs font-semibold uppercase tracking-[0.18em] ${
          dark ? "text-white/60" : "text-slate"
        }`}
      >
        Subscribe in under 10 seconds
      </label>
      <form
        onSubmit={onSubmit}
        className={`flex w-full flex-col gap-3 rounded-2xl p-2 sm:flex-row ${wrapperClass} ${
          compact ? "max-w-md" : "max-w-xl"
        } transition duration-300 hover:-translate-y-0.5 hover:shadow-editorial`}
      >
        <input
          id={inputId}
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Enter your work email"
          className={`min-h-14 flex-1 rounded-xl border border-transparent bg-transparent px-4 text-sm outline-none ring-0 focus:border-accent/30 focus:ring-0 ${inputClass}`}
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className={`min-h-14 rounded-xl px-6 text-sm font-semibold ${buttonClass} disabled:cursor-not-allowed disabled:opacity-70`}
        >
          {status === "loading" ? "Submitting..." : "Subscribe"}
        </button>
      </form>
      <div
        className={`mt-4 rounded-2xl px-4 py-3 text-sm leading-7 transition-all duration-300 ${feedbackClass}`}
      >
        {status === "success" ? (
          <div className="space-y-1">
            <p className="font-semibold">Check your inbox to confirm your subscription.</p>
            <p>{message}</p>
          </div>
        ) : status === "error" ? (
          <p>{message}</p>
        ) : (
          <p>Enter your email, verify once, and receive OmniBrief daily.</p>
        )}
      </div>
    </div>
  );
}
