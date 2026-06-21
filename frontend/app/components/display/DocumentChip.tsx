"use client";

import { useState, CSSProperties } from "react";

interface DocumentChipProps {
  name?: string;
  meta?: string;
  status?: "indexed" | "processing" | "error";
  active?: boolean;
  onClick?: () => void;
  onRemove?: () => void;
  style?: CSSProperties;
}

export function DocumentChip({
  name = "document.pdf",
  meta,
  status = "indexed",
  active = false,
  onClick,
  onRemove,
  style,
}: DocumentChipProps) {
  const [hover, setHover] = useState(false);

  const statusColors: Record<string, string> = {
    indexed: "var(--confidence-high)",
    processing: "var(--confidence-med)",
    error: "var(--confidence-low)",
  };

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: "flex", alignItems: "center", gap: 10,
        padding: "8px 10px",
        background: active ? "var(--brand-subtle)" : (hover ? "var(--paper-100)" : "transparent"),
        border: `1px solid ${active ? "var(--indigo-200)" : "transparent"}`,
        borderRadius: "var(--radius-md)",
        cursor: onClick ? "pointer" : "default",
        transition: "background var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out)",
        ...style,
      }}
    >
      <span style={{
        width: 30, height: 30, flexShrink: 0, borderRadius: "var(--radius-sm)",
        background: "var(--confidence-low-bg)", color: "var(--confidence-low)",
        display: "inline-flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 3v4a1 1 0 0 0 1 1h4" />
          <path d="M5 8V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-2" />
          <path d="M3 13h7M3 13l2-2M3 13l2 2" />
        </svg>
      </span>
      <span style={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 0, flex: 1 }}>
        <span style={{
          fontFamily: "var(--font-sans)", fontSize: "var(--text-sm)", fontWeight: "var(--weight-semibold)",
          color: "var(--text-strong)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>{name}</span>
        {meta && (
          <span style={{
            display: "inline-flex", alignItems: "center", gap: 5,
            fontFamily: "var(--font-mono)", fontSize: "var(--text-2xs)", color: "var(--text-muted)",
          }}>
            <span style={{ width: 5, height: 5, borderRadius: "50%", background: statusColors[status] }} />
            {meta}
          </span>
        )}
      </span>
      {onRemove && hover && (
        <button
          aria-label="Remove"
          onClick={(e) => { e.stopPropagation(); onRemove(); }}
          style={{
            border: "none", background: "transparent", cursor: "pointer", color: "var(--text-faint)",
            display: "flex", padding: 4, borderRadius: "var(--radius-xs)", lineHeight: 0,
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
        </button>
      )}
    </div>
  );
}
