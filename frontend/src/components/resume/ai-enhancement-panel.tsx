'use client'

import { useState, useEffect } from 'react'
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
import { useAIEnhancement, AISuggestion } from '@/hooks/use-ai-enhancement'
import { ResumeSection } from '@/stores/resume.store'
import { cn } from '@/lib/utils'
import { TruthVerificationBadge } from './truth-verification-badge'
import { InterviewTalkingPoints } from './interview-talking-points'
import { MetricConfirmationDialog } from './metric-confirmation-dialog'

interface AIEnhancementPanelProps {
    open: boolean
    onClose: () => void
    section: ResumeSection | undefined
    onApplySuggestion: (suggestion: string) => void
}

export function AIEnhancementPanel({
    open,
    onClose,
    section,
    onApplySuggestion,
}: AIEnhancementPanelProps) {
    const [activeTab, setActiveTab] = useState('suggestions')
    const [confirmingSuggestion, setConfirmingSuggestion] = useState<{
        index: number
        suggestion: AISuggestion
    } | null>(null)

    const {
        suggestions,
        isLoading,
        error,
        fetchEnhancements,
        regenerate,
        appliedSuggestions,
        markAsApplied,
        setSuggestions
    } = useAIEnhancement(section?.id)

    // Initial fetch when panel opens
    useEffect(() => {
        if (open && section) {
            let content = ""
            let type: "summary" | "bullet_point" | "description" = "bullet_point"

            if (section.type === 'summary') {
                content = section.content as string
                type = "summary"
            } else if (section.type === 'experience') {
                // For experience, we take the first achievement or description
                const experiences = section.content as any[]
                const firstExp = experiences?.[0]
                content = firstExp?.achievements?.[0] || firstExp?.description || ""
                type = "bullet_point"
            }

            if (content && suggestions.length === 0) {
                fetchEnhancements(content, type)
            }
        }
    }, [open, section, fetchEnhancements, suggestions.length])

    const handleApplyClick = (suggestion: AISuggestion, index: number) => {
        if (suggestion.verification_status === 'needs_confirmation') {
            setConfirmingSuggestion({ index, suggestion })
        } else {
            onApplySuggestion(suggestion.enhanced_text)
            markAsApplied(index)
        }
    }

    const handleConfirmMetrics = (responses: Record<string, string>) => {
        if (!confirmingSuggestion) return

        let updatedText = confirmingSuggestion.suggestion.enhanced_text
        Object.entries(responses).forEach(([metric, value]) => {
            updatedText = updatedText.replace(metric, value)
        })

        onApplySuggestion(updatedText)
        markAsApplied(confirmingSuggestion.index)

        // Update the suggestion in local state so it looks applied/verified
        const newSuggestions = [...suggestions]
        newSuggestions[confirmingSuggestion.index] = {
            ...confirmingSuggestion.suggestion,
            enhanced_text: updatedText,
            verification_status: 'verified'
        }
        setSuggestions(newSuggestions)
        setConfirmingSuggestion(null)
    }

    return (
        <>
            <Sheet open={open} onOpenChange={onClose}>
                <SheetContent className="w-[550px] sm:max-w-[550px] border-l border-slate-200 shadow-2xl">
                    <SheetHeader>
                        <SheetTitle className="flex items-center gap-2 text-xl text-slate-900">
                            <Sparkles className="h-6 w-6 text-indigo-500 fill-indigo-100" />
                            Grounded AI Enhancement
                        </SheetTitle>
                        <SheetDescription className="text-slate-500">
                            Factual, defensible improvements grounded in your Persona.
                        </SheetDescription>
                    </SheetHeader>

                    {error && (
                        <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-100 flex items-center gap-2 text-rose-800 text-sm font-medium">
                            <AlertTriangle className="h-4 w-4" />
                            {error}
                        </div>
                    )}

                    <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
                        <TabsList className="grid w-full grid-cols-3 bg-slate-100 p-1 rounded-xl">
                            <TabsTrigger value="suggestions" className="rounded-lg">Suggestions</TabsTrigger>
                            <TabsTrigger value="keywords" className="rounded-lg">Keywords</TabsTrigger>
                            <TabsTrigger value="metrics" className="rounded-lg">Analytics</TabsTrigger>
                        </TabsList>

                        <TabsContent value="suggestions" className="mt-4 outline-none">
                            <ScrollArea className="h-[calc(100vh-250px)]">
                                <div className="space-y-6 pr-4 pb-8">
                                    {isLoading ? (
                                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                                            <div className="relative">
                                                <RefreshCw className="h-10 w-10 animate-spin text-indigo-500" />
                                                <Sparkles className="h-4 w-4 text-amber-500 absolute -top-1 -right-1" />
                                            </div>
                                            <p className="text-sm font-medium text-slate-500 animate-pulse">Verifying facts against your Persona...</p>
                                        </div>
                                    ) : suggestions.length === 0 ? (
                                        <div className="py-20 text-center space-y-2">
                                            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-dashed border-slate-200">
                                                <Sparkles className="w-8 h-8 text-slate-300" />
                                            </div>
                                            <p className="text-slate-500 font-medium">No suggestions yet.</p>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => {
                                                    let content = ""
                                                    if (section?.type === 'summary') content = section.content as string
                                                    else if (section?.type === 'experience') content = (section.content as any[])?.[0]?.achievements?.[0] || ""

                                                    if (content) fetchEnhancements(content, section?.type === 'summary' ? 'summary' : 'bullet_point')
                                                }}
                                            >
                                                Generate Suggestions
                                            </Button>
                                        </div>
                                    ) : (
                                        suggestions.map((suggestion, index) => (
                                            <Card
                                                key={index}
                                                className={cn(
                                                    'group border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all duration-300',
                                                    appliedSuggestions.includes(index) && 'border-emerald-500 bg-emerald-50/30'
                                                )}
                                            >
                                                <CardContent className="p-5 space-y-4">
                                                    <div className="flex justify-between items-start border-b border-slate-100 pb-3">
                                                        <TruthVerificationBadge
                                                            status={suggestion.verification_status}
                                                            confidence={suggestion.confidence_score}
                                                            sourceFields={suggestion.source_persona_fields}
                                                            defensibilityScore={suggestion.defensibility_score}
                                                        />
                                                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                                                            {suggestion.enhancement_type}
                                                        </span>
                                                    </div>

                                                    <div className="space-y-3">
                                                        <div className="space-y-1.5 opacity-60">
                                                            <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Original</span>
                                                            <p className="text-sm text-slate-600 italic">"{suggestion.original_text}"</p>
                                                        </div>

                                                        <div className="relative py-1">
                                                            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white border border-slate-100 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10">
                                                                <ArrowRight className="h-4 w-4 text-indigo-500" />
                                                            </div>
                                                            <div className="h-px bg-slate-100 w-full" />
                                                        </div>

                                                        <div className="space-y-1.5">
                                                            <span className="text-[10px] font-bold uppercase text-indigo-500 tracking-wider">Enhanced & Grounded</span>
                                                            <p className="text-md font-semibold text-slate-900 leading-snug">"{suggestion.enhanced_text}"</p>
                                                        </div>
                                                    </div>

                                                    <InterviewTalkingPoints points={suggestion.interview_talking_points} />

                                                    <div className="flex justify-end gap-2 pt-2">
                                                        {appliedSuggestions.includes(index) ? (
                                                            <div className="flex items-center gap-1.5 text-emerald-600 font-bold text-xs bg-emerald-100/50 px-3 py-1.5 rounded-full">
                                                                <Check className="h-3.5 w-3.5" />
                                                                Applied to CV
                                                            </div>
                                                        ) : (
                                                            <Button
                                                                size="sm"
                                                                className={cn(
                                                                    "rounded-full px-6 font-bold shadow-sm transition-all",
                                                                    suggestion.verification_status === 'needs_confirmation'
                                                                        ? "bg-blue-600 hover:bg-blue-700 text-white"
                                                                        : "bg-indigo-600 hover:bg-indigo-700 text-white"
                                                                )}
                                                                onClick={() => handleApplyClick(suggestion, index)}
                                                            >
                                                                {suggestion.verification_status === 'needs_confirmation' ? 'Confirm & Apply' : 'Apply Suggestion'}
                                                            </Button>
                                                        )}
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        ))
                                    )}
                                </div>
                            </ScrollArea>

                            <div className="pt-6 border-t mt-4">
                                <Button
                                    variant="outline"
                                    onClick={() => {
                                        let content = ""
                                        if (section?.type === 'summary') content = section.content as string
                                        else if (section?.type === 'experience') content = (section.content as any[])?.[0]?.achievements?.[0] || ""

                                        if (content) regenerate(content, section?.type === 'summary' ? 'summary' : 'bullet_point')
                                    }}
                                    disabled={isLoading}
                                    className="w-full gap-2 rounded-xl py-6 font-bold text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 border-slate-200 transition-all border-dashed"
                                >
                                    <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
                                    Regenerate Truthful Suggestions
                                </Button>
                            </div>
                        </TabsContent>

                        <TabsContent value="keywords">
                            <div className="p-10 text-center space-y-4">
                                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto border border-dashed border-slate-200 opacity-50">
                                    <Sparkles className="w-8 h-8 text-slate-300" />
                                </div>
                                <div className="space-y-1">
                                    <p className="text-slate-500 font-bold">Keyword Optimization</p>
                                    <p className="text-xs text-slate-400">Target specific job descriptions while remaining grounded.</p>
                                </div>
                                <Badge variant="secondary" className="bg-slate-100 text-slate-500 border-none">Coming Soon</Badge>
                            </div>
                        </TabsContent>

                        <TabsContent value="metrics">
                            <div className="p-10 text-center space-y-4">
                                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto border border-dashed border-slate-200 opacity-50">
                                    <RefreshCw className="w-8 h-8 text-slate-300" />
                                </div>
                                <div className="space-y-1">
                                    <p className="text-slate-500 font-bold">Smart Analytics</p>
                                    <p className="text-xs text-slate-400">Discover hidden metrics in your experience.</p>
                                </div>
                                <Badge variant="secondary" className="bg-slate-100 text-slate-500 border-none">Coming Soon</Badge>
                            </div>
                        </TabsContent>
                    </Tabs>
                </SheetContent>
            </Sheet>

            {confirmingSuggestion && (
                <MetricConfirmationDialog
                    open={!!confirmingSuggestion}
                    onClose={() => setConfirmingSuggestion(null)}
                    onConfirm={handleConfirmMetrics}
                    originalText={confirmingSuggestion.suggestion.original_text}
                    suggestedText={confirmingSuggestion.suggestion.enhanced_text}
                    questions={[
                        {
                            metric: confirmingSuggestion.suggestion.enhanced_text.match(/\d+[%$x]/g)?.[0] || "percentage",
                            question: confirmingSuggestion.suggestion.confirmation_prompt || "Please confirm the exact number for this achievement.",
                            input_type: "text"
                        }
                    ]}
                />
            )}
        </>
    )
}
