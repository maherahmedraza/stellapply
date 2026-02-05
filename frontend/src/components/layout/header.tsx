"use client";

import { useState, useRef, useEffect } from "react";
import { User, Settings, LogOut, ChevronDown } from "lucide-react";
import Link from "next/link";
import { logout } from "@/lib/auth";

import { ThemeToggle } from "@/components/ui/theme-toggle";

interface UserInfo {
    name?: string | null;
    email?: string | null;
    image?: string | null;
}

function UserMenu({ user }: { user: UserInfo }) {
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    // Close menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleLogout = async () => {
        await logout();
    };

    return (
        <div ref={menuRef} className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 wobble border-2 border-pencil-black bg-white dark:bg-muted-paper hover:bg-ink-blue hover:text-white transition-all group"
            >
                <div className="w-8 h-8 wobble bg-ink-blue/20 flex items-center justify-center text-ink-blue group-hover:bg-white/20 group-hover:text-white">
                    <User className="w-5 h-5" strokeWidth={2.5} />
                </div>
                <span className="font-handwritten text-lg hidden sm:block">
                    {user?.name || "Space Cadet"}
                </span>
                <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 wobble border-3 border-pencil-black bg-white dark:bg-muted-paper shadow-sketch-lg z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-4 border-b-2 border-dashed border-pencil-black/20">
                        <p className="font-marker text-lg truncate">{user?.name || "Space Cadet"}</p>
                        <p className="font-handwritten text-sm text-pencil-black/60 truncate">
                            {user?.email || "cadet@stellapply.ai"}
                        </p>
                    </div>

                    <div className="p-2">
                        <Link
                            href="/dashboard/settings"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center gap-3 px-3 py-2 font-handwritten text-lg hover:bg-ink-blue hover:text-white transition-colors wobble"
                        >
                            <Settings className="w-5 h-5" />
                            Settings
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-3 py-2 font-handwritten text-lg text-marker-red hover:bg-marker-red hover:text-white transition-colors wobble"
                        >
                            <LogOut className="w-5 h-5" />
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export function Header({ user }: { user: UserInfo }) {
    return (
        <header className="h-16 bg-paper-bg border-b-3 border-pencil-black flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
                <span className="font-marker text-xl text-pencil-black">
                    Welcome, <span className="text-ink-blue">{user?.name || "Space Cadet"}</span>
                </span>
            </div>

            <div className="flex items-center gap-4">
                <ThemeToggle />
                <UserMenu user={user} />
            </div>
        </header>
    );
}
