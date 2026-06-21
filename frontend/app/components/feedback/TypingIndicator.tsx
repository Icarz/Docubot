"use client";

import { CSSProperties } from "react";

interface TypingIndicatorProps {
  label?: string;
  style?: CSSProperties;
}

export function TypingIndicator({ label, style }: TypingIndicatorProps) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8, ...style }}>
      <span style={{ display: "inline-flex", gap: 4, alignItems: "center" }} aria-label="DocuBot is thinking">
        {[0, 1, 2].map((i) => (
          <span key={i} style={{
            width: 7, height: 7, borderRadius: "50%", background: "var(--brand)",
            animation: `docubot-bounce 1.2s ${i * 0.16}s infinite`,
          }} />
        ))}
      </span>
      {label && (
        <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{label}</span>
      )}
    </span>
  );
}
