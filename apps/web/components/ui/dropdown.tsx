"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/components/ui/cn";

interface DropdownProps {
  label: ReactNode;
  children: ReactNode;
  align?: "left" | "right";
  className?: string;
}

export function Dropdown({ label, children, align = "left", className }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handlePointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, []);

  return (
    <div ref={rootRef} className={cn("relative inline-flex", className)}>
      <Button variant="secondary" onClick={() => setOpen((current) => !current)} aria-haspopup="menu" aria-expanded={open}>
        {label}
        <span className="text-xs text-muted-foreground">⌄</span>
      </Button>
      {open ? (
        <div className={cn("absolute top-12 z-40 min-w-48 rounded-2xl border border-border bg-panel/95 p-2 shadow-2xl shadow-background/40 backdrop-blur", align === "right" ? "right-0" : "left-0")} role="menu">
          {children}
        </div>
      ) : null}
    </div>
  );
}

interface DropdownItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  destructive?: boolean;
}

export function DropdownItem({ className, destructive, ...props }: DropdownItemProps) {
  return (
    <button
      className={cn(
        "flex w-full items-center rounded-xl px-3 py-2 text-left text-sm transition hover:bg-surface",
        destructive ? "text-danger-foreground" : "text-foreground",
        className
      )}
      role="menuitem"
      type="button"
      {...props}
    />
  );
}
