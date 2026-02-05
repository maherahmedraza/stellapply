"use client"

import React from "react"
import { MessageSquare, ExternalLink, Lightbulb } from "lucide-react"
import { cn } from "@/lib/utils"

interface InterviewTalkingPointsProps {
    points: string[]
    className?: string
}

export function InterviewTalkingPoints({ points, className }: InterviewTalkingPointsProps) {
    if (!points || points.length === 0) return null

    return (
        <div className={cn("mt-4 space-y-3", className)}>
            <div className="flex items-center gap-2 text-[11px] font-heading uppercase tracking-wider text-foreground-subtle">
                <MessageSquare className="w-3.5 h-3.5" />
                Interview Prep Points
            </div>

            <div className="grid gap-2">
                {points.map((point, idx) => (
                    <div
                        key={idx}
                        className={cn(
                            "group flex items-start gap-2.5 p-3",
                            "wobbly-sm border-2 border-border",
                            "bg-success/5 hover:bg-success/10 transition-all cursor-default"
                        )}
                    >
                        <div className="mt-1 flex-shrink-0">
                            <Lightbulb className="w-3.5 h-3.5 text-success" />
                        </div>
                        <p className="text-[12px] leading-relaxed text-foreground-muted group-hover:text-foreground transition-colors font-body">
                            {point}
                        </p>
                    </div>
                ))}
            </div>

            <p className="text-[10px] text-foreground-subtle italic flex items-center gap-1 font-body">
                <ExternalLink className="w-3 h-3" />
                These points are linked to your verified Persona facts.
            </p>
        </div>
    )
}
