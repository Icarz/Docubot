"use client";

import { CSSProperties } from "react";

interface AvatarProps {
  kind?: "user" | "bot";
  name?: string;
  src?: string;
  size?: "xs" | "sm" | "md" | "lg";
  style?: CSSProperties;
}

export function Avatar({ kind = "user", name = "", src, size = "md", style }: AvatarProps) {
  const sizes: Record<string, number> = { xs: 24, sm: 30, md: 38, lg: 48 };
  const d = sizes[size] || sizes.md;
  const fontSize = Math.round(d * 0.4);

  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");

  const base: CSSProperties = {
    width: d, height: d, flexShrink: 0,
    borderRadius: "var(--radius-md)",
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    fontFamily: "var(--font-display)", fontWeight: "var(--weight-semibold)",
    fontSize, overflow: "hidden", userSelect: "none", lineHeight: 1,
    ...style,
  };

  if (kind === "bot") {
    return (
      <span style={{ ...base, background: "var(--brand)", color: "#fff" }}>
        <svg width={d * 0.56} height={d * 0.56} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="8" width="16" height="11" rx="3" />
          <path d="M12 8V4M9 4h6" />
          <circle cx="9" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
          <circle cx="15" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
        </svg>
      </span>
    );
  }

  if (src) {
    return <img src={src} alt={name} style={{ ...base, objectFit: "cover" }} />;
  }

  return (
    <span style={{ ...base, background: "var(--paper-200)", color: "var(--ink-700)" }}>
      {initials || "?"}
    </span>
  );
}
