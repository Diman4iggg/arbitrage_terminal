import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react"

import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: Array<string | false | null | undefined>) {
  return twMerge(clsx(inputs))
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn("rounded-lg border border-terminal-700 bg-terminal-900", className)}>{children}</section>
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("border-b border-terminal-700 px-4 py-3", className)}>{children}</div>
}

export function CardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("p-4", className)}>{children}</div>
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode
  tone?: "success" | "warning" | "danger" | "neutral"
}) {
  const tones = {
    success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    warning: "border-amber-500/30 bg-amber-500/10 text-amber-300",
    danger: "border-rose-500/30 bg-rose-500/10 text-rose-300",
    neutral: "border-zinc-700 bg-zinc-800/60 text-zinc-300",
  }
  return <span className={cn("inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium", tones[tone])}>{children}</span>
}

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn("rounded-md border border-terminal-700 bg-terminal-800 px-3 py-2 text-xs font-medium text-zinc-200 transition hover:border-zinc-600 hover:bg-terminal-700 disabled:cursor-not-allowed disabled:opacity-50", className)}
      {...props}
    />
  )
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn("w-full rounded-md border border-terminal-700 bg-terminal-950 px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-emerald-500/60", className)}
      {...props}
    />
  )
}

export function Select({ className, children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn("rounded-md border border-terminal-700 bg-terminal-950 px-3 py-2 text-sm text-zinc-200 outline-none focus:border-emerald-500/60", className)} {...props}>
      {children}
    </select>
  )
}

export function Switch({ checked, onChange, label }: { checked: boolean; onChange: (checked: boolean) => void; label: string }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={cn("relative h-5 w-9 rounded-full border transition", checked ? "border-emerald-500/60 bg-emerald-500/30" : "border-zinc-700 bg-zinc-800")}
    >
      <span className={cn("absolute top-0.5 h-3.5 w-3.5 rounded-full bg-zinc-100 transition", checked ? "left-[18px]" : "left-0.5")} />
    </button>
  )
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded bg-terminal-700/70", className)} />
}
