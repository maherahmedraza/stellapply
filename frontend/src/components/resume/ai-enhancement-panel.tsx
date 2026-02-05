'use client'

import { useState, useEffect, useCallback } from 'react'
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Sparkles, Check, RefreshCw, ArrowRight, AlertTriangle } from 'lucide-react'
import { useTruthfulEnhancement, TruthfulEnhancement } from '@/hooks/use-truthful-enhancement'
import { ResumeSection, ExperienceContent } from '@/stores/resume.store'
import { cn } from '@/lib/utils'
import { TruthVerificationBadge, VerificationStatus } from './truth-verification-badge'
import { InterviewTalkingPoints } from './interview-talking-points'
import { MetricConfirmationDialog } from './metric-confirmation-dialog'

interface AIEnhancementPanelProps {
    open: boolean
    onClose: () => void
    section: ResumeSection | undefined
    onApplySuggestion: (suggestion: string) => void
}

type EnhancementType = 'summary' | 'bullet_point' | 'description'

/**
 * Extract content and type from a resume section for AI enhancement
 */
function extractSectionContent(section: ResumeSection): { content: string; type: EnhancementType } {
    if (section.type === 'summary') {
        return {
            content: section.content as string,
            type: 'summary'
        }
    }

    if (section.type === 'experience') {
        const experiences = section.content as ExperienceContent[]
        const firstExp = experiences?.[0]
        const content = firstExp?.achievements?.[0] || firstExp?.description || ''
        return { content, type: 'bullet_point' }
    }

    return { content: '', type: 'description' }
}

export function AIEnhancementPanel({
    open,
    onClose,
    section,
    onApplySuggestion,
}: AIEnhancementPanelProps) {
    const [activeTab, setActiveTab] = useState('suggestions')
    const [isApplied, setIsApplied] = useState(false)
    const [hasInitiallyFetched, setHasInitiallyFetched] = useState(false)
    const [showConfirmation, setShowConfirmation] = useState(false)

    const {
        enhance,
        confirmPlaceholders,
        enhancement,
        isLoading,
        error,
        clearEnhancement
    } = useTruthfulEnhancement()

    // Reset state when section changes
    useEffect(() => {
        if (section?.id) {
            setHasInitiallyFetched(false)
            setIsApplied(false)
            clearEnhancement()
        }
    }, [section?.id, clearEnhancement])

    // Fetch enhancements when panel opens
    useEffect(() => {
        if (!open || !section || hasInitiallyFetched) return

        const { content, type } = extractSectionContent(section)

        if (content) {
            enhance(content, type)
            setHasInitiallyFetched(true)
        }
    }, [open, section, hasInitiallyFetched, enhance])

    const handleApplyClick = useCallback((suggestion: TruthfulEnhancement) => {
        if (suggestion.verificationStatus === 'needs_confirmation') {
            setShowConfirmation(true)
        } else {
            onApplySuggestion(suggestion.enhancedText)
            setIsApplied(true)
        }
    }, [onApplySuggestion])

    const handleConfirmMetrics = useCallback(async (responses: Record<string, string>) => {
        if (!enhancement) return

        try {
            // In a real app we'd need an ID, but for current single-flow we simulate it
            const finalText = await confirmPlaceholders("active-enhancement", responses)
            onApplySuggestion(finalText)
            setIsApplied(true)
            setShowConfirmation(false)
        } catch (err) {
            console.error("Failed to confirm metrics", err)
        }
    }, [enhancement, confirmPlaceholders, onApplySuggestion])

    const handleRegenerate = useCallback(() => {
        if (!section) return
        const { content, type } = extractSectionContent(section)
        if (content) {
            enhance(content, type)
            setIsApplied(false)
        }
    }, [section, enhance])

    return (
        <>
            <Sheet open={open} onOpenChange={onClose}>
                <SheetContent
                    className={cn(
                        "w-[550px] sm:max-w-[550px]",
                        "border-l-[3px] border-border",
                        "bg-background-alt",
                        "shadow-hand-xl"
                    )}
                >
                    <SheetHeader>
                        <SheetTitle className="flex items-center gap-3 font-heading text-2xl text-foreground">
                            <div className="p-2 wobbly-sm bg-accent/10 border-2 border-accent/20">
                                <Sparkles className="h-6 w-6 text-accent" />
                            </div>
                            Grounded AI Enhancement
                        </SheetTitle>
                        <SheetDescription className="text-foreground-muted font-body text-base">
                            Truthful, fact-checked improvements grounded in your Persona.
                        </SheetDescription>
                    </SheetHeader>

                    {error && (
                        <div className={cn(
                            "mt-4 p-4 flex items-center gap-3",
                            "wobbly-sm border-2 border-error",
                            "bg-error/5 text-error",
                            "font-body text-sm"
                        )}>
                            <AlertTriangle className="h-5 w-5 shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
                        <TabsList className={cn(
                            "grid w-full grid-cols-3 p-1",
                            "bg-background-muted",
                            "border-2 border-border",
                            "wobbly-md shadow-hand-sm"
                        )}>
                            <TabsTrigger
                                value="suggestions"
                                className="wobbly-sm font-heading font-bold data-[state=active]:bg-background-alt data-[state=active]:shadow-hand-sm data-[state=active]:border-2 data-[state=active]:border-border"
                            >
                                Suggestions
                            </TabsTrigger>
                            <TabsTrigger
                                value="keywords"
                                className="wobbly-sm font-heading font-bold data-[state=active]:bg-background-alt data-[state=active]:shadow-hand-sm data-[state=active]:border-2 data-[state=active]:border-border"
                            >
                                Keywords
                            </TabsTrigger>
                            <TabsTrigger
                                value="metrics"
                                className="wobbly-sm font-heading font-bold data-[state=active]:bg-background-alt data-[state=active]:shadow-hand-sm data-[state=active]:border-2 data-[state=active]:border-border"
                            >
                                Analytics
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="suggestions" className="mt-6 outline-none">
                            <ScrollArea className="h-[calc(100vh-320px)]">
                                <div className="space-y-6 pr-4 pb-8">
                                    {isLoading ? (
                                        <LoadingState />
                                    ) : !enhancement ? (
                                        <EmptyState onGenerate={handleRegenerate} />
                                    ) : (
                                        <div className="space-y-6">
                                            <SuggestionCard
                                                suggestion={enhancement}
                                                isApplied={isApplied}
                                                onApply={handleApplyClick}
                                            />

                                            {/* Defensibility Insight Card */}
                                            <Card variant="sticky" className="p-4 space-y-2">
                                                <h4 className="font-heading text-lg flex items-center gap-2">
                                                    <RefreshCw className="h-4 w-4 text-accent-secondary" />
                                                    Truth Verification Logic
                                                </h4>
                                                <p className="text-sm font-body text-foreground-muted">
                                                    This suggestion was cross-referenced against your records in
                                                    <span className="font-bold"> {enhancement.sourcePersonaFields.join(", ")}</span>.
                                                    The AI ensured no unverified skills were added.
                                                </p>
                                            </Card>
                                        </div>
                                    )}
                                </div>
                            </ScrollArea>

                            <div className="pt-4 border-t-2 border-dashed border-border">
                                <Button
                                    variant="outline"
                                    onClick={handleRegenerate}
                                    disabled={isLoading}
                                    className="w-full gap-2 py-6 wobbly-md shadow-hand-sm"
                                >
                                    <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
                                    Regenerate Truthful Suggestions
                                </Button>
                            </div>
                        </TabsContent>

                        <TabsContent value="keywords">
                            <ComingSoonState
                                title="Keyword Optimization"
                                description="Target specific job descriptions while remaining grounded."
                            />
                        </TabsContent>

                        <TabsContent value="metrics">
                            <ComingSoonState
                                title="Smart Analytics"
                                description="Discover hidden metrics in your experience."
                            />
                        </TabsContent>
                    </Tabs>
                </SheetContent>
            </Sheet>

            {showConfirmation && enhancement && (
                <MetricConfirmationDialog
                    open={true}
                    onClose={() => setShowConfirmation(false)}
                    onConfirm={handleConfirmMetrics}
                    originalText={enhancement.originalText}
                    suggestedText={enhancement.enhancedText}
                    questions={extractMetricQuestions(enhancement)}
                />
            )}
        </>
    )
}

// ============================================
// Sub-components
// ============================================

function LoadingState() {
    return (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="relative">
                <div className="p-6 wobbly-circle bg-background-muted border-2 border-border shadow-hand-sm">
                    <RefreshCw className="h-10 w-10 animate-spin text-accent" />
                </div>
                <Sparkles className="h-5 w-5 text-accent-warning absolute -top-1 -right-1" />
            </div>
            <p className="text-foreground-muted font-heading text-lg animate-pulse">
                Fact-checking against Persona...
            </p>
        </div>
    )
}

function EmptyState({ onGenerate }: { onGenerate: () => void }) {
    return (
        <div className="py-20 text-center space-y-6">
            <div className={cn(
                "w-24 h-24 mx-auto",
                "flex items-center justify-center",
                "wobbly-circle border-2 border-dashed border-border",
                "bg-background-muted"
            )}>
                <Sparkles className="w-10 h-10 text-foreground-subtle" />
            </div>
            <div className="space-y-2">
                <p className="text-foreground-muted font-heading text-xl">
                    Truthful AI is Ready
                </p>
                <p className="text-foreground-subtle font-body">
                    We'll only suggest improvements we can prove.
                </p>
            </div>
            <Button
                variant="default"
                onClick={onGenerate}
                className="mt-6 shadow-hand-md"
            >
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Verification
            </Button>
        </div>
    )
}

interface SuggestionCardProps {
    suggestion: TruthfulEnhancement
    isApplied: boolean
    onApply: (suggestion: TruthfulEnhancement) => void
}

function SuggestionCard({ suggestion, isApplied, onApply }: SuggestionCardProps) {
    return (
        <Card
            className={cn(
                'group wobbly-md border-[3px] border-border shadow-hand-md transition-all',
                isApplied && 'border-success bg-success/5 shadow-none'
            )}
        >
            <CardContent className="p-6 space-y-5">
                {/* Status Bar */}
                <div className="flex items-center justify-between border-b-2 border-dashed border-border/50 pb-4">
                    <TruthVerificationBadge
                        status={suggestion.verificationStatus as VerificationStatus}
                        confidence={suggestion.confidenceScore}
                        sourceFields={suggestion.sourcePersonaFields}
                        defensibilityScore={suggestion.defensibilityScore}
                    />
                    <div className="flex gap-1">
                        <Badge variant="outline" className="text-[10px] wobbly-sm font-heading border-border/30">
                            {suggestion.enhancementType}
                        </Badge>
                    </div>
                </div>

                {/* Content Comparison */}
                <div className="space-y-4">
                    {/* Original */}
                    <div className="bg-background-muted/30 p-3 wobbly-sm border border-border/10">
                        <span className="text-[10px] font-heading uppercase text-foreground-subtle tracking-wider mb-1 block">
                            Original Content
                        </span>
                        <p className="text-sm text-foreground-muted italic font-body">
                            "{suggestion.originalText}"
                        </p>
                    </div>

                    {/* Arrow Divider */}
                    <div className="flex justify-center -my-2 relative z-10">
                        <div className="bg-background-alt border-2 border-border wobbly-circle p-1 shadow-hand-sm">
                            <ArrowRight className="h-4 w-4 text-accent" />
                        </div>
                    </div>

                    {/* Enhanced */}
                    <div className="p-3 wobbly-md border-2 border-accent/20 bg-accent/5">
                        <span className="text-[10px] font-heading uppercase text-accent tracking-widest mb-1 block">
                            Grounded Improvement
                        </span>
                        <p className="text-lg font-heading text-foreground leading-tight">
                            "{suggestion.enhancedText}"
                        </p>
                    </div>
                </div>

                {/* Interview Prep Section */}
                {suggestion.interviewTalkingPoints && suggestion.interviewTalkingPoints.length > 0 && (
                    <div className="pt-2">
                        <InterviewTalkingPoints points={suggestion.interviewTalkingPoints} />
                    </div>
                )}

                {/* Action Button */}
                <div className="flex justify-end pt-2">
                    {isApplied ? (
                        <div className={cn(
                            "flex items-center gap-2",
                            "px-6 py-3",
                            "wobbly-button border-2 border-success",
                            "bg-success/10 text-success",
                            "font-heading font-bold"
                        )}>
                            <Check className="h-5 w-5" />
                            Applied to Resume
                        </div>
                    ) : (
                        <Button
                            size="lg"
                            variant={suggestion.verificationStatus === 'needs_confirmation' ? 'secondary' : 'default'}
                            onClick={() => onApply(suggestion)}
                            className="wobbly-button px-8 shadow-hand-md"
                        >
                            {suggestion.verificationStatus === 'needs_confirmation'
                                ? 'Confirm Values'
                                : 'Accept Enhancement'
                            }
                        </Button>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}

function ComingSoonState({ title, description }: { title: string; description: string }) {
    return (
        <div className="py-20 text-center space-y-4">
            <div className={cn(
                "w-20 h-20 mx-auto",
                "flex items-center justify-center",
                "wobbly-circle border-2 border-dashed border-border",
                "bg-background-muted opacity-50"
            )}>
                <Sparkles className="w-8 h-8 text-foreground-subtle" />
            </div>
            <div className="space-y-2">
                <p className="text-foreground-muted font-heading text-xl">{title}</p>
                <p className="text-foreground-subtle font-body text-base">{description}</p>
            </div>
            <Badge variant="outline" className="wobbly-sm border-dashed">Module Locked</Badge>
        </div>
    )
}

/**
 * Extract metric questions from a suggestion for the confirmation dialog
 */
function extractMetricQuestions(suggestion: TruthfulEnhancement) {
    const metrics = suggestion.enhancedText.match(/\[.*?\]|\d+[%$x]/g) || []

    return metrics.slice(0, 3).map(metric => ({
        metric,
        question: suggestion.confirmationPrompt || `What was the specific value for "${metric}"?`,
        input_type: 'text' as const
    }))
}
