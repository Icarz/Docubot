"use client";

import { useState, CSSProperties } from "react";

interface SourceCitationProps {
  quote: string;
  section?: string;
  page?: number;
  index?: number;
  onJump?: () => void;
  style?: CSSProperties;
}

export function SourceCitation({ quote, section, page, index, onJump, style }: SourceCitationProps) {
  const [hover, setHover] = useState(false);

  return (
    <div
      onClick={onJump}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        position: "relative",
        display: "flex", flexDirection: "column", gap: 6,
        padding: "10px 12px 10px 14px",
        background: hover && onJump ? "var(--highlight-100)" : "var(--paper-50)",
        borderRadius: "var(--radius-sm)",
        borderLeft: "3px solid var(--accent)",
        cursor: onJump ? "pointer" : "default",
        transition: "background var(--dur-fast) var(--ease-out)",
        ...style,
      }}
    >
      <span style={{
        fontFamily: "var(--font-serif)", fontStyle: "italic",
        fontSize: "var(--text-sm)", lineHeight: "var(--leading-relaxed)",
        color: "var(--text-body)",
      }}>
        {typeof index === "number" && (
          <span style={{
            fontFamily: "var(--font-mono)", fontStyle: "normal", fontSize: "var(--text-2xs)",
            fontWeight: "var(--weight-semibold)", color: "var(--highlight-500)", marginRight: 6,
          }}>[{index}]</span>
        )}
        &ldquo;{quote}&rdquo;
      </span>
      {(section || page) && (
        <span style={{
          display: "inline-flex", alignItems: "center", gap: 6,
          fontFamily: "var(--font-mono)", fontSize: "var(--text-2xs)",
          color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "var(--tracking-wide)",
        }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          {section}{section && page ? " · " : ""}{page ? `p. ${page}` : ""}
        </span>
      )}
    </div>
  );
}
