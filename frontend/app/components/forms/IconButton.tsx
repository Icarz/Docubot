"use client";

import { useState, ButtonHTMLAttributes, ReactNode } from "react";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "accent";
  size?: "sm" | "md" | "lg";
  active?: boolean;
  children: ReactNode;
}

export function IconButton({
  children,
  variant = "ghost",
  size = "md",
  disabled = false,
  active = false,
  onClick,
  style,
  ...rest
}: IconButtonProps) {
  const [hover, setHover] = useState(false);
  const [pressed, setPressed] = useState(false);

  const dims: Record<string, number> = { sm: 30, md: 38, lg: 46 };
  const d = dims[size] || dims.md;

  const palettes: Record<string, { base: React.CSSProperties; hover: React.CSSProperties }> = {
    primary: { base: { background: "var(--brand)", color: "#fff" }, hover: { background: "var(--brand-hover)" } },
    secondary: { base: { background: "var(--surface-card)", color: "var(--text-strong)", border: "1px solid var(--border-default)" }, hover: { background: "var(--paper-50)", border: "1px solid var(--border-strong)" } },
    ghost: { base: { background: active ? "var(--paper-200)" : "transparent", color: "var(--text-body)" }, hover: { background: "var(--paper-100)" } },
    accent: { base: { background: "var(--accent)", color: "var(--accent-ink)" }, hover: { background: "var(--highlight-400)" } },
  };
  const p = palettes[variant] || palettes.ghost;

  return (
    <button
      disabled={disabled}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => { setHover(false); setPressed(false); }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center",
        width: d, height: d, padding: 0,
        borderRadius: "var(--radius-sm)", border: "1px solid transparent",
        cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.45 : 1,
        lineHeight: 0,
        transition: "background var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out)",
        transform: pressed && !disabled ? "scale(0.92)" : "none",
        ...p.base,
        ...(hover && !disabled ? p.hover : null),
        ...style,
      }}
      {...rest}
    >
      {children}
    </button>
  );
}
