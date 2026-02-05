"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
    const [isDark, setIsDark] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        // Check localStorage or system preference
        const stored = localStorage.getItem("theme");
        if (stored === "dark") {
            setIsDark(true);
            document.documentElement.classList.add("dark");
        } else if (stored === "light") {
            setIsDark(false);
            document.documentElement.classList.remove("dark");
        } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            setIsDark(true);
            document.documentElement.classList.add("dark");
        }
    }, []);

    const toggleTheme = () => {
        const newDark = !isDark;
        setIsDark(newDark);
        if (newDark) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    };

    if (!mounted) return null;

    return (
        <button
            onClick={toggleTheme}
            className="p-2 wobble border-2 border-pencil-black bg-white dark:bg-muted-paper hover:bg-ink-blue hover:text-white transition-all"
            aria-label="Toggle dark mode"
        >
            {isDark ? (
                <Sun className="w-5 h-5" strokeWidth={2.5} />
            ) : (
                <Moon className="w-5 h-5" strokeWidth={2.5} />
            )}
        </button>
    );
}
