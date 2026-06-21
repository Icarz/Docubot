"use client";

import { CSSProperties, ReactNode } from "react";
import { Avatar } from "../display/Avatar";
import { ConfidenceBadge } from "../feedback/ConfidenceBadge";
import { SourceCitation } from "./SourceCitation";

export interface Source {
  quote: string;
  section?: string;
  page?: number;
}

interface MessageBubbleProps {
  role?: "user" | "assistant";
  children: ReactNode;
  confidence?: "high" | "medium" | "low";
  section?: string;
  sources?: Source[];
  showAvatar?: boolean;
  style?: CSSProperties;
}

export function MessageBubble({
  role = "assistant",
  children,
  confidence,
  section,
  sources = [],
  showAvatar = true,
  style,
}: MessageBubbleProps) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, ...style }}>
        <div style={{
          maxWidth: "min(78%, 560px)",
          background: "var(--brand)", color: "var(--text-on-brand)",
          padding: "11px 15px",
          borderRadius: "var(--radius-lg) var(--radius-lg) var(--radius-xs) var(--radius-lg)",
          fontFamily: "var(--font-sans)", fontSize: "var(--text-base)", lineHeight: "var(--leading-normal)",
          boxShadow: "var(--shadow-xs)", wordBreak: "break-word",
        }}>
          {children}
        </div>
      </div>
    );
  }

  const hasHeader = confidence || section;

  return (
    <div style={{ display: "flex", gap: 10, alignItems: "flex-start", ...style }}>
      {showAvatar && <Avatar kind="bot" size="md" />}
      <div style={{
        maxWidth: "min(84%, 620px)", flex: 1, minWidth: 0,
        background: "var(--surface-card)", border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-xs) var(--radius-lg) var(--radius-lg) var(--radius-lg)",
        boxShadow: "var(--shadow-sm)", overflow: "hidden",
      }}>
        {hasHeader && (
          <div style={{
            display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap",
            padding: "10px 16px", borderBottom: "1px solid var(--border-subtle)",
            background: "var(--paper-50)",
          }}>
            {confidence && <ConfidenceBadge level={confidence} size="sm" />}
            {section && (
              <span style={{
                display: "inline-flex", alignItems: "center", gap: 5,
                fontFamily: "var(--font-mono)", fontSize: "var(--text-2xs)", color: "var(--text-muted)",
                textTransform: "uppercase", letterSpacing: "var(--tracking-wide)",
              }}>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg>
                {section}
              </span>
            )}
          </div>
        )}
        <div style={{
          padding: "14px 16px",
          fontFamily: "var(--font-serif)", fontSize: "var(--text-md)",
          lineHeight: "var(--leading-relaxed)", color: "var(--text-strong)",
        }}>
          {children}
        </div>
        {sources.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "0 16px 14px" }}>
            <span style={{
              fontFamily: "var(--font-sans)", fontSize: "var(--text-2xs)", fontWeight: "var(--weight-bold)",
              color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "var(--tracking-caps)",
            }}>Sources</span>
            {sources.map((s, i) => (
              <SourceCitation key={i} index={i + 1} quote={s.quote} section={s.section} page={s.page} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
