"use client";

import { CSSProperties } from "react";

interface ConfidenceBadgeProps {
  level?: "high" | "medium" | "low";
  showLabel?: boolean;
  size?: "sm" | "md";
  style?: CSSProperties;
}

export function ConfidenceBadge({ level = "high", showLabel = true, size = "md", style }: ConfidenceBadgeProps) {
  const key = String(level).toLowerCase() as "high" | "medium" | "low";
  const config: Record<string, { label: string; fg: string; bg: string; dots: number }> = {
    high:   { label: "High confidence", fg: "var(--confidence-high)", bg: "var(--confidence-high-bg)", dots: 3 },
    medium: { label: "Medium confidence", fg: "var(--confidence-med)", bg: "var(--confidence-med-bg)", dots: 2 },
    low:    { label: "Low confidence", fg: "var(--confidence-low)", bg: "var(--confidence-low-bg)", dots: 1 },
  };
  const c = config[key] || config.high;

  const sizes: Record<string, { fontSize: string; pad: string; dot: number; gap: number; height: number }> = {
    sm: { fontSize: "var(--text-2xs)", pad: "3px 8px", dot: 5, gap: 5, height: 20 },
    md: { fontSize: "var(--text-xs)", pad: "4px 10px", dot: 6, gap: 6, height: 24 },
  };
  const s = sizes[size] || sizes.md;

  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: s.gap,
      height: s.height, padding: s.pad,
      background: c.bg, color: c.fg,
      fontFamily: "var(--font-sans)", fontSize: s.fontSize, fontWeight: "var(--weight-semibold)",
      borderRadius: "var(--radius-full)", whiteSpace: "nowrap", lineHeight: 1,
      ...style,
    }}>
      <span style={{ display: "inline-flex", gap: 2, alignItems: "center" }} aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <span key={i} style={{
            width: s.dot, height: s.dot, borderRadius: "50%",
            background: i < c.dots ? "currentColor" : "transparent",
            border: "1.5px solid currentColor", opacity: i < c.dots ? 1 : 0.35,
            boxSizing: "border-box",
          }} />
        ))}
      </span>
      {showLabel && c.label}
    </span>
  );
}
