"use client";

import { useState, useEffect } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://omni.tanish.website";

export default function ContactModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  // Prevent scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
  }, [isOpen]);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("loading");
    setError("");

    try {
      const resp = await fetch(`${API_BASE_URL}/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.detail || "Failed to send message.");
      }

      setStatus("success");
      setFormData({ name: "", email: "", message: "" });
      setTimeout(() => {
        setIsOpen(false);
        setStatus("idle");
      }, 3000);
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  }

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="text-sm text-slate hover:text-ink transition-colors"
      >
        Contact
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-ink/40 backdrop-blur-sm transition-opacity"
            onClick={() => setIsOpen(false)}
          />

          {/* Modal Card */}
          <div className="relative w-full max-w-lg transform overflow-hidden rounded-[2rem] border border-mist bg-white p-8 shadow-editorial transition-all animate-in fade-in zoom-in duration-300">
            <div className="flex items-center justify-between border-b border-mist pb-6">
              <div>
                <h2 className="font-heading text-2xl font-bold text-ink">
                  Get in touch
                </h2>
                <p className="mt-1 text-sm text-slate">
                  Send a message directly to the OmniBrief team.
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-full p-2 text-slate hover:bg-paper hover:text-ink transition-colors"
              >
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-6">
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase tracking-[0.18em] text-slate">
                    Name
                  </label>
                  <input
                    required
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    placeholder="Your name"
                    className="w-full rounded-xl border border-mist bg-paper px-4 py-3 text-sm outline-none transition-all focus:border-accent/30 focus:bg-white focus:ring-4 focus:ring-accent/5"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase tracking-[0.18em] text-slate">
                    Email
                  </label>
                  <input
                    required
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    placeholder="Your email"
                    className="w-full rounded-xl border border-mist bg-paper px-4 py-3 text-sm outline-none transition-all focus:border-accent/30 focus:bg-white focus:ring-4 focus:ring-accent/5"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-[0.18em] text-slate">
                  Message
                </label>
                <textarea
                  required
                  rows={4}
                  value={formData.message}
                  onChange={(e) =>
                    setFormData({ ...formData, message: e.target.value })
                  }
                  placeholder="How can we help?"
                  className="w-full resize-none rounded-xl border border-mist bg-paper px-4 py-3 text-sm outline-none transition-all focus:border-accent/30 focus:bg-white focus:ring-4 focus:ring-accent/5"
                />
              </div>

              {status === "error" && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900">
                  {error}
                </div>
              )}

              {status === "success" && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
                  <p className="font-bold">Message sent successfully!</p>
                  <p className="mt-1">We will contact you within 24 hours.</p>
                </div>
              )}

              <button
                type="submit"
                disabled={status === "loading" || status === "success"}
                className="w-full rounded-xl bg-ink px-6 py-4 text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#262626] hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-70"
              >
                {status === "loading" ? "Sending..." : "Send Message"}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
