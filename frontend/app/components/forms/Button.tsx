"use client";

import { useState, ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "accent" | "danger";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  loading?: boolean;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  fullWidth = false,
  disabled = false,
  loading = false,
  leadingIcon,
  trailingIcon,
  type = "button",
  onClick,
  style,
  ...rest
}: ButtonProps) {
  const [hover, setHover] = useState(false);
  const [active, setActive] = useState(false);

  const sizes: Record<string, { padding: string; height: number; fontSize: string; gap: number; radius: string }> = {
    sm: { padding: "0 12px", height: 32, fontSize: "var(--text-sm)", gap: 6, radius: "var(--radius-sm)" },
    md: { padding: "0 16px", height: 40, fontSize: "var(--text-base)", gap: 8, radius: "var(--radius-md)" },
    lg: { padding: "0 22px", height: 50, fontSize: "var(--text-md)", gap: 10, radius: "var(--radius-md)" },
  };
  const s = sizes[size] || sizes.md;

  const palettes: Record<string, { base: React.CSSProperties; hover: React.CSSProperties; active: React.CSSProperties }> = {
    primary: {
      base: { background: "var(--brand)", color: "var(--text-on-brand)", border: "1px solid transparent", boxShadow: "var(--shadow-xs)" },
      hover: { background: "var(--brand-hover)" },
      active: { background: "var(--brand-active)" },
    },
    secondary: {
      base: { background: "var(--surface-card)", color: "var(--text-strong)", border: "1px solid var(--border-default)", boxShadow: "var(--shadow-xs)" },
      hover: { background: "var(--paper-50)", border: "1px solid var(--border-strong)" },
      active: { background: "var(--paper-100)" },
    },
    ghost: {
      base: { background: "transparent", color: "var(--text-body)", border: "1px solid transparent" },
      hover: { background: "var(--paper-100)" },
      active: { background: "var(--paper-200)" },
    },
    accent: {
      base: { background: "var(--accent)", color: "var(--accent-ink)", border: "1px solid transparent", boxShadow: "var(--shadow-xs)" },
      hover: { background: "var(--highlight-400)" },
      active: { background: "var(--highlight-500)" },
    },
    danger: {
      base: { background: "var(--danger)", color: "#fff", border: "1px solid transparent", boxShadow: "var(--shadow-xs)" },
      hover: { background: "#BE3E35" },
      active: { background: "#A8362E" },
    },
  };
  const p = palettes[variant] || palettes.primary;

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => { setHover(false); setActive(false); }}
      onMouseDown={() => setActive(true)}
      onMouseUp={() => setActive(false)}
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center",
        gap: s.gap, height: s.height, padding: s.padding,
        width: fullWidth ? "100%" : "auto",
        fontFamily: "var(--font-sans)", fontSize: s.fontSize,
        fontWeight: "var(--weight-semibold)", letterSpacing: "var(--tracking-snug)",
        lineHeight: 1, borderRadius: s.radius,
        cursor: disabled || loading ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        transition: "background var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out)",
        transform: active && !disabled ? "translateY(1px) scale(0.99)" : "none",
        whiteSpace: "nowrap", userSelect: "none",
        ...p.base,
        ...(hover && !disabled && !loading ? p.hover : null),
        ...(active && !disabled && !loading ? p.active : null),
        ...style,
      }}
      {...rest}
    >
      {loading && <Spinner />}
      {!loading && leadingIcon}
      {children}
      {!loading && trailingIcon}
    </button>
  );
}

function Spinner() {
  return (
    <span style={{
      width: 15, height: 15, borderRadius: "50%",
      border: "2px solid currentColor", borderTopColor: "transparent",
      display: "inline-block", animation: "docubot-spin 0.7s linear infinite", opacity: 0.85,
    }} />
  );
}
