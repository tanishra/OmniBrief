"use client";

import { useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://omni.tanish.website";

export default function SubscribeForm({ compact = false, dark = false }) {
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
    ? "bg-paper text-ink hover:bg-white"
    : "bg-ink text-white hover:bg-[#262626]";

  return (
    <div className="w-full">
      <form
        onSubmit={onSubmit}
        className={`flex w-full flex-col gap-3 rounded-2xl p-2 sm:flex-row ${wrapperClass} ${
          compact ? "max-w-md" : "max-w-xl"
        }`}
      >
        <input
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
      <p
        className={`mt-3 text-sm ${
          dark ? "text-white/70" : "text-slate"
        }`}
      >
        {message ||
          "Enter your email, verify once, and receive OmniBrief daily."}
      </p>
    </div>
  );
}
