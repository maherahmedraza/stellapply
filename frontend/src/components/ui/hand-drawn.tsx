"use client";

import React from "react";
import { cn } from "@/lib/utils";

/**
 * SketchButton - A wobbly, hand-drawn style button
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "accent";
}

export const SketchButton = ({
    className,
    variant = "primary",
    children,
    ...props
}: ButtonProps) => {
    const variantStyles = {
        primary: "bg-white text-pencil-black border-pencil-black hover:bg-ink-blue hover:text-white",
        secondary: "bg-muted-paper text-pencil-black border-pencil-black hover:bg-ink-blue hover:text-white",
        accent: "bg-marker-red text-white border-pencil-black hover:bg-marker-red/90",
    };

    return (
        <button
            className={cn(
                "wobble border-[3px] px-6 py-2 text-lg font-bold shadow-sketch transition-all duration-100",
                "active:shadow-none active:translate-x-[4px] active:translate-y-[4px]",
                "hover:shadow-sketch-sm hover:translate-x-[2px] hover:translate-y-[2px] hover:scale-[1.02]",
                variantStyles[variant],
                className
            )}
            {...props}
        >
            {children}
        </button>
    );
};

/**
 * SketchCard - A paper-like container with optional decorations
 */
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    decoration?: "tape" | "tack" | "none";
    color?: "white" | "yellow";
}

export const SketchCard = ({
    className,
    decoration = "none",
    color = "white",
    children,
    ...props
}: CardProps) => {
    return (
        <div
            className={cn(
                "relative wobble-md border-[3px] border-pencil-black p-6 shadow-sketch-sm transition-transform hover:rotate-1",
                color === "white" ? "bg-white" : "bg-postit-yellow",
                className
            )}
            {...props}
        >
            {decoration === "tape" && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-24 h-8 bg-zinc-400/30 -rotate-2 border border-black/10 z-10" />
            )}
            {decoration === "tack" && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-6 h-6 bg-marker-red rounded-full shadow-inner z-10 border-2 border-pencil-black">
                    <div className="absolute top-1 left-1 w-2 h-2 bg-white/40 rounded-full" />
                </div>
            )}
            {children}
        </div>
    );
};

/**
 * SketchInput - A hand-drawn input field
 */
export const SketchInput = ({
    className,
    ...props
}: React.InputHTMLAttributes<HTMLInputElement>) => {
    return (
        <input
            className={cn(
                "wobble border-[3px] border-pencil-black px-4 py-3 bg-white text-pencil-black",
                "focus:outline-none focus:border-ink-blue focus:ring-4 focus:ring-ink-blue/10",
                "placeholder:text-pencil-black/40 font-handwritten text-xl",
                className
            )}
            {...props}
        />
    );
};
/**
 * SketchCheckbox - A hand-drawn style checkbox
 */
export const SketchCheckbox = ({
    label,
    checked,
    onChange,
    className,
}: {
    label: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
    className?: string;
}) => {
    return (
        <label className={cn("flex items-start gap-3 cursor-pointer group", className)}>
            <div
                onClick={() => onChange(!checked)}
                className={cn(
                    "w-6 h-6 wobble border-[3px] border-pencil-black flex items-center justify-center transition-all bg-white shadow-sketch-sm",
                    checked && "bg-ink-blue border-ink-blue shadow-none"
                )}
            >
                {checked && <div className="w-2.5 h-2.5 bg-white rotate-45 transform" />}
            </div>
            <span className="text-lg font-handwritten text-pencil-black/80 group-hover:text-pencil-black select-none leading-tight pt-0.5">
                {label}
            </span>
        </label>
    );
};
