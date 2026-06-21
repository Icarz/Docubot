"use client";

import { useState, useRef, useEffect, CSSProperties, ChangeEvent } from "react";
import { IconButton } from "../forms/IconButton";

interface ComposerProps {
  value: string;
  onChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: (value: string) => void;
  onAttach?: () => void;
  placeholder?: string;
  disabled?: boolean;
  attachedName?: string;
  style?: CSSProperties;
}

export function Composer({
  value,
  onChange,
  onSend,
  onAttach,
  placeholder = "Ask a question about your document…",
  disabled = false,
  attachedName,
  style,
}: ComposerProps) {
  const [focus, setFocus] = useState(false);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const hasText = value && value.trim().length > 0;

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
  }, [value]);

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (hasText && !disabled) onSend(value);
    }
  };

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      background: "var(--surface-card)",
      border: `1.5px solid ${focus ? "var(--border-focus)" : "var(--border-default)"}`,
      borderRadius: "var(--radius-xl)",
      boxShadow: focus ? "var(--shadow-focus)" : "var(--shadow-sm)",
      transition: "border-color var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out)",
      padding: "8px 8px 8px 8px",
      ...style,
    }}>
      {attachedName && (
        <div style={{
          display: "inline-flex", alignSelf: "flex-start", alignItems: "center", gap: 6,
          margin: "2px 4px 8px", padding: "4px 10px",
          background: "var(--brand-subtle)", borderRadius: "var(--radius-full)",
          fontFamily: "var(--font-mono)", fontSize: "var(--text-2xs)", color: "var(--brand-subtle-text)",
        }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 3v4a1 1 0 0 0 1 1h4" /><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /></svg>
          {attachedName}
        </div>
      )}
      <div style={{ display: "flex", alignItems: "flex-end", gap: 8 }}>
        {onAttach && (
          <IconButton aria-label="Attach PDF" variant="ghost" onClick={onAttach}>
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" /></svg>
          </IconButton>
        )}
        <textarea
          ref={taRef}
          rows={1}
          value={value}
          onChange={onChange}
          onKeyDown={handleKey}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          placeholder={placeholder}
          disabled={disabled}
          style={{
            flex: 1, resize: "none", border: "none", outline: "none", background: "transparent",
            fontFamily: "var(--font-sans)", fontSize: "var(--text-base)", lineHeight: "var(--leading-normal)",
            color: "var(--text-strong)", padding: "8px 4px", maxHeight: 160, overflowY: "auto",
          }}
        />
        <IconButton
          aria-label="Send"
          variant={hasText ? "primary" : "ghost"}
          disabled={!hasText || disabled}
          onClick={() => hasText && onSend(value)}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 19V5M5 12l7-7 7 7" /></svg>
        </IconButton>
      </div>
    </div>
  );
}
