"use client"

import React from "react"
import {
    CheckCircle2,
    AlertCircle,
    HelpCircle,
    XCircle,
    Info,
    ShieldCheck
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"

export type VerificationStatus = "verified" | "plausible" | "needs_confirmation" | "rejected"

interface TruthVerificationBadgeProps {
    status: VerificationStatus
    confidence?: number
    sourceFields?: string[]
    defensibilityScore?: number
    className?: string
    showLabel?: boolean
}

const STATUS_CONFIG = {
    verified: {
        badgeVariant: 'success' as const,
        icon: CheckCircle2,
        label: "Verified",
        description: "This enhancement is fully grounded in your verified persona data.",
    },
    plausible: {
        badgeVariant: 'warning' as const,
        icon: Info,
        label: "Plausible",
        description: "This enhancement is reasonable but couldn't be fully verified.",
    },
    needs_confirmation: {
        badgeVariant: 'secondary' as const,
        icon: HelpCircle,
        label: "Confirm Needed",
        description: "Please verify the specific numbers or details before applying.",
    },
    rejected: {
        badgeVariant: 'error' as const,
        icon: XCircle,
        label: "Fact Warning",
        description: "This enhancement contains claims we couldn't verify.",
    },
} as const

export function TruthVerificationBadge({
    status,
    confidence,
    sourceFields = [],
    defensibilityScore,
    className,
    showLabel = true,
}: TruthVerificationBadgeProps) {
    const config = STATUS_CONFIG[status]
    const Icon = config.icon

    const defensibilityLevel = defensibilityScore !== undefined
        ? defensibilityScore > 0.8 ? 'high'
            : defensibilityScore > 0.5 ? 'medium'
                : 'low'
        : null

    const defensibilityColors = {
        high: 'text-success',
        medium: 'text-accent-warning',
        low: 'text-error',
    }

    return (
        <TooltipProvider>
            <div className={cn("flex flex-col gap-2", className)}>
                <div className="flex items-center gap-3 flex-wrap">
                    {/* Main Status Badge */}
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div>
                                <Badge
                                    variant={config.badgeVariant}
                                    className="cursor-help"
                                >
                                    <Icon className="w-3.5 h-3.5" />
                                    {showLabel && <span>{config.label}</span>}
                                </Badge>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent
                            side="top"
                            className="max-w-xs wobbly-sm border-2 border-border bg-background-alt shadow-hand-md"
                        >
                            <div className="space-y-2 p-1">
                                <p className="font-heading text-sm">{config.label}</p>
                                <p className="font-body text-xs text-foreground-muted">
                                    {config.description}
                                </p>
                                {sourceFields.length > 0 && (
                                    <div className="pt-2 border-t border-dashed border-border">
                                        <p className="text-[10px] uppercase tracking-wider text-foreground-subtle font-heading">
                                            Source Fields:
                                        </p>
                                        <p className="text-xs font-body text-foreground-muted">
                                            {sourceFields.join(", ")}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </TooltipContent>
                    </Tooltip>

                    {/* Confidence Score */}
                    {confidence !== undefined && (confidence > 0) && (
                        <span className="text-[11px] font-body text-foreground-subtle">
                            {Math.round(confidence * 100)}% confident
                        </span>
                    )}

                    {/* Defensibility Score */}
                    {defensibilityLevel && (
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className={cn(
                                    "flex items-center gap-1 text-[11px] font-body cursor-help",
                                    defensibilityColors[defensibilityLevel]
                                )}>
                                    <ShieldCheck className="w-3.5 h-3.5" />
                                    <span>{Math.round((defensibilityScore ?? 0) * 100)}% Interview-ready</span>
                                </div>
                            </TooltipTrigger>
                            <TooltipContent
                                side="top"
                                className="wobbly-sm border-2 border-border bg-background-alt shadow-hand-md"
                            >
                                <p className="font-body text-xs">
                                    How well you can defend this claim in an interview
                                </p>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </div>

                {/* Confirmation Warning */}
                {status === "needs_confirmation" && (
                    <p className="text-[11px] text-accent-secondary font-body italic flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        Fact needs your confirmation before applying
                    </p>
                )}
            </div>
        </TooltipProvider>
    )
}
