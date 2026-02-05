'use client'

import React, { useState } from 'react'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AlertTriangle, CheckCircle, HelpCircle, ArrowRight } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Text, Heading } from '@/components/ui/typography'
import { Badge } from '@/components/ui/badge'

// Export this type so it can be used by the parent component
export interface TruthfulEnhancement {
    originalText: string
    enhancedText: string
    requiresVerification: boolean
    verificationPrompt?: string
    metricsArePlaceholder: boolean
    groundingExplanation: string
    enhancementType: string
}

export function TruthfulEnhancementModal({
    enhancement,
    onAccept,
    onReject,
    onVerify
}: {
    enhancement: TruthfulEnhancement
    onAccept: (text: string) => void
    onReject: () => void
    onVerify: (verifiedText: string) => void
}) {
    const [placeholderValues, setPlaceholderValues] = useState<Record<string, string>>({})

    // Extract placeholders like [X%], [N users]
    const placeholders = enhancement.enhancedText.match(/\[.*?\]/g) || []

    const handleVerify = () => {
        let finalText = enhancement.enhancedText

        // Replace placeholders with user-provided values
        Object.entries(placeholderValues).forEach(([placeholder, value]) => {
            finalText = finalText.replace(placeholder, value)
        })

        onVerify(finalText)
    }

    return (
        <Dialog open onOpenChange={(open) => !open && onReject()}>
            <DialogContent className="max-w-2xl border-2 border-border shadow-hand-lg bg-background-alt overflow-hidden">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-3 font-heading text-2xl">
                        {enhancement.requiresVerification || placeholders.length > 0 ? (
                            <>
                                <div className="p-2 wobbly-sm bg-accent-warning/10 text-accent-warning">
                                    <AlertTriangle className="h-6 w-6" />
                                </div>
                                <span>Verification Required</span>
                            </>
                        ) : (
                            <>
                                <div className="p-2 wobbly-sm bg-accent/10 text-accent">
                                    <CheckCircle className="h-6 w-6" />
                                </div>
                                <span>Truthful AI Enhancement</span>
                            </>
                        )}
                    </DialogTitle>
                    <DialogDescription className="text-foreground-muted font-body mt-2">
                        Our AI has sketched an improvement based on your verified persona.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 pt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Original */}
                        <div className="p-4 wobbly-sm border-2 border-border bg-background flex flex-col">
                            <Badge variant="outline" className="self-start mb-2 uppercase text-[10px] tracking-widest opacity-50">
                                Original
                            </Badge>
                            <Text variant="muted" className="italic">"{enhancement.originalText}"</Text>
                        </div>

                        {/* Enhanced */}
                        <div className="p-4 wobbly-sm border-2 border-accent/30 bg-accent/5 flex flex-col relative">
                            <Badge variant="primary" className="self-start mb-2 uppercase text-[10px] tracking-widest">
                                AI Sketch
                            </Badge>
                            <ArrowRight className="absolute -left-6 top-1/2 -translate-y-1/2 text-accent/30 hidden md:block" />
                            <Text className="font-bold">{enhancement.enhancedText}</Text>
                        </div>
                    </div>

                    {/* Truthfulness Explanation */}
                    <Card variant="default" className="bg-background-muted/30 border-dashed border-2 border-border">
                        <CardContent className="p-4 flex items-start gap-3">
                            <HelpCircle className="h-5 w-5 text-accent shrink-0 mt-0.5" />
                            <div className="space-y-1">
                                <Heading level="h5" className="text-sm">Why this is truthful:</Heading>
                                <Text variant="muted" className="text-sm leading-relaxed">
                                    {enhancement.groundingExplanation}
                                </Text>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Placeholder Verification */}
                    {placeholders.length > 0 && (
                        <div className="p-6 wobbly-md border-2 border-accent-warning/30 bg-accent-warning/5 space-y-4">
                            <Heading level="h4" className="text-accent-warning text-lg flex items-center gap-2">
                                ⚠️ Fill in the Details
                            </Heading>
                            <Text variant="muted" size="sm">
                                To keep your resume 100% honest, please provide the actual numbers or details for these placeholders:
                            </Text>
                            <div className="space-y-3">
                                {placeholders.map((placeholder) => (
                                    <div key={placeholder} className="flex flex-col sm:flex-row sm:items-center gap-3">
                                        <span className="text-xs font-heading bg-background-muted px-3 py-1 wobbly-sm border border-border shrink-0">
                                            {placeholder}
                                        </span>
                                        <Input
                                            placeholder={`Provide value (e.g., 25% or 5,000)`}
                                            value={placeholderValues[placeholder] || ''}
                                            onChange={(e) => setPlaceholderValues(prev => ({
                                                ...prev,
                                                [placeholder]: e.target.value
                                            }))}
                                            className="flex-1 w-full"
                                        />
                                    </div>
                                ))}
                            </div>
                            <Text variant="subtle" size="sm" className="italic mt-4 opacity-70">
                                Tip: Only use metrics you can defend in a real interview.
                            </Text>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t-2 border-dashed border-border mt-6">
                        <Button variant="outline" onClick={onReject} className="shadow-none">
                            Keep Original Sketch
                        </Button>
                        {placeholders.length > 0 ? (
                            <Button
                                onClick={handleVerify}
                                disabled={placeholders.some(p => !placeholderValues[p] || placeholderValues[p].trim() === '')}
                                className="shadow-hand-md"
                            >
                                Apply with My Values
                            </Button>
                        ) : (
                            <Button onClick={() => onAccept(enhancement.enhancedText)} className="shadow-hand-md">
                                Accept Enhancement
                            </Button>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
