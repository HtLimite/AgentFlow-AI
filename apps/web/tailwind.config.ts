import type { Config } from "tailwindcss";

const withOpacity = (variable: string) => `hsl(var(${variable}) / <alpha-value>)`;

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: withOpacity("--color-background"),
        foreground: withOpacity("--color-foreground"),
        surface: withOpacity("--color-surface"),
        "surface-strong": withOpacity("--color-surface-strong"),
        panel: withOpacity("--color-panel"),
        border: withOpacity("--color-border"),
        "border-strong": withOpacity("--color-border-strong"),
        muted: withOpacity("--color-muted"),
        "muted-foreground": withOpacity("--color-muted-foreground"),
        primary: withOpacity("--color-primary"),
        "primary-foreground": withOpacity("--color-primary-foreground"),
        "primary-soft": "hsl(var(--color-primary) / 0.12)",
        success: withOpacity("--color-success"),
        "success-foreground": withOpacity("--color-success-foreground"),
        "success-soft": "hsl(var(--color-success) / 0.12)",
        warning: withOpacity("--color-warning"),
        "warning-foreground": withOpacity("--color-warning-foreground"),
        "warning-soft": "hsl(var(--color-warning) / 0.14)",
        danger: withOpacity("--color-danger"),
        "danger-foreground": withOpacity("--color-danger-foreground"),
        "danger-soft": "hsl(var(--color-danger) / 0.14)",
        info: withOpacity("--color-info"),
        "info-foreground": withOpacity("--color-info-foreground"),
        "info-soft": "hsl(var(--color-info) / 0.12)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem"
      }
    }
  },
  plugins: []
};

export default config;
