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
            <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <MessageSquare className="w-3.5 h-3.5" />
                Interview Prep Points
            </div>

            <div className="grid gap-2">
                {points.map((point, idx) => (
                    <div
                        key={idx}
                        className="group flex items-start gap-2.5 p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100/50 hover:bg-emerald-50 hover:border-emerald-200 transition-all cursor-default"
                    >
                        <div className="mt-1 flex-shrink-0">
                            <Lightbulb className="w-3.5 h-3.5 text-emerald-500" />
                        </div>
                        <p className="text-[12px] leading-relaxed text-slate-600 group-hover:text-slate-900 transition-colors">
                            {point}
                        </p>
                    </div>
                ))}
            </div>

            <p className="text-[10px] text-slate-400 italic flex items-center gap-1">
                <ExternalLink className="w-3 h-3" />
                These points are linked to your verified Persona facts.
            </p>
        </div>
    )
}
