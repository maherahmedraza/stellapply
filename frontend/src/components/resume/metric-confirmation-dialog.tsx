"use client"

import React, { useState } from "react"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, HelpCircle } from "lucide-react"

interface MetricQuestion {
    metric: string
    question: string
    input_type: string
}

interface MetricConfirmationDialogProps {
    open: boolean
    onClose: () => void
    onConfirm: (responses: Record<string, string>) => void
    originalText: string
    suggestedText: string
    questions: MetricQuestion[]
}

export function MetricConfirmationDialog({
    open,
    onClose,
    onConfirm,
    originalText,
    suggestedText,
    questions
}: MetricConfirmationDialogProps) {
    const [responses, setResponses] = useState<Record<string, string>>({})

    const handleInputChange = (metric: string, value: string) => {
        setResponses(prev => ({
            ...prev,
            [metric]: value
        }))
    }

    const handleConfirm = () => {
        onConfirm(responses)
        onClose()
    }

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[550px] bg-white border-slate-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-slate-900">
                        <HelpCircle className="w-5 h-5 text-blue-500" />
                        Confirm Suggested Metrics
                    </DialogTitle>
                    <DialogDescription className="text-slate-500">
                        The AI suggested quantitative improvements. Please confirm the exact numbers from your experience.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {/* Comparison View */}
                    <div className="grid gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <div className="space-y-1.5">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Original</span>
                            <p className="text-sm text-slate-600 italic">"{originalText}"</p>
                        </div>
                        <div className="h-px bg-slate-200" />
                        <div className="space-y-1.5">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-500">AI Suggested</span>
                            <p className="text-sm font-medium text-slate-900">"{suggestedText}"</p>
                        </div>
                    </div>

                    {/* Questions */}
                    <div className="space-y-4">
                        {questions.map((q, idx) => (
                            <div key={idx} className="space-y-2 p-3 rounded-lg border border-blue-100 bg-blue-50/30">
                                <Label className="text-sm font-semibold text-slate-800">
                                    {q.question}
                                </Label>
                                <div className="flex gap-2">
                                    <Input
                                        className="bg-white border-slate-200 focus:ring-blue-500"
                                        placeholder={`e.g. ${q.metric}`}
                                        type={q.input_type === "number" ? "text" : "text"}
                                        value={responses[q.metric] || ""}
                                        onChange={(e) => handleInputChange(q.metric, e.target.value)}
                                    />
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="text-[10px] h-9"
                                        onClick={() => handleInputChange(q.metric, q.metric.replace(/[^\d.%$]/g, ""))}
                                    >
                                        Keep Suggestion
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-50 border border-amber-100">
                        <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5" />
                        <p className="text-[11px] text-amber-800 leading-relaxed">
                            <strong>Why verify?</strong> Accurate metrics make your resume drastically more defensible in interviews.
                            Only use numbers you can explain and back up with evidence.
                        </p>
                    </div>
                </div>

                <DialogFooter className="gap-2 sm:gap-0">
                    <Button variant="ghost" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button
                        className="bg-slate-900 text-white hover:bg-slate-800"
                        onClick={handleConfirm}
                        disabled={Object.keys(responses).length < questions.length}
                    >
                        Verify & Apply
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
