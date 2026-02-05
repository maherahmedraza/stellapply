"use client"

import React from "react"
import { CheckCircle2, AlertCircle, HelpCircle, XCircle, Info, ShieldCheck } from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export type VerificationStatus = "verified" | "plausible" | "needs_confirmation" | "rejected"

interface TruthVerificationBadgeProps {
    status: VerificationStatus
    confidence?: number
    sourceFields?: string[]
    defensibilityScore?: number
    className?: string
    showLabel?: boolean
}

export function TruthVerificationBadge({
    status,
    confidence,
    sourceFields = [],
    defensibilityScore = 1.0,
    className,
    showLabel = true,
}: TruthVerificationBadgeProps) {

    const statusConfig = {
        verified: {
            color: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
            icon: <CheckCircle2 className="w-3.5 h-3.5" />,
            label: "Verified",
        },
        plausible: {
            color: "bg-amber-500/10 text-amber-500 border-amber-500/20",
            icon: <Info className="w-3.5 h-3.5" />,
            label: "Plausible",
        },
        needs_confirmation: {
            color: "bg-blue-500/10 text-blue-500 border-blue-500/20",
            icon: <HelpCircle className="w-3.5 h-3.5" />,
            label: "Confirm Needed",
        },
        rejected: {
            color: "bg-rose-500/10 text-rose-500 border-rose-500/20",
            icon: <XCircle className="w-3.5 h-3.5" />,
            label: "Fact Warning",
        },
    }

    const config = statusConfig[status]

    return (
        <div className={cn("flex flex-col gap-1.5", className)}>
            <div className="flex items-center gap-2">
                <Badge
                    variant="outline"
                    className={cn(
                        "flex items-center gap-1.5 px-2 py-0.5 rounded-full font-medium transition-all group relative",
                        config.color
                    )}
                >
                    {config.icon}
                    {showLabel && <span>{config.label}</span>}

                    {/* Tooltip for source fields */}
                    {sourceFields.length > 0 && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                            <div className="bg-slate-900 text-white text-[10px] px-2 py-1 rounded shadow-lg whitespace-nowrap border border-slate-800">
                                Source: {sourceFields.join(", ")}
                            </div>
                        </div>
                    )}
                </Badge>

                {defensibilityScore !== undefined && (
                    <div className="flex items-center gap-1 text-[11px] font-medium text-slate-500">
                        <ShieldCheck className={cn(
                            "w-3 h-3",
                            defensibilityScore > 0.8 ? "text-emerald-500" :
                                defensibilityScore > 0.5 ? "text-amber-500" : "text-rose-500"
                        )} />
                        <span>{Math.round(defensibilityScore * 100)}% Interview-ready</span>
                    </div>
                )}
            </div>

            {status === "needs_confirmation" && (
                <p className="text-[10px] text-blue-500/80 italic animate-pulse">
                    * Fact needs your confirmation before applying
                </p>
            )}
        </div>
    )
}
