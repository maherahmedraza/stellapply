import { useState, useCallback } from 'react'
import { resumeApi } from '@/lib/api/resume'
import { TruthfulEnhancement } from '@/components/resume/truthful-enhancement-modal'

export function useTruthfulEnhancement() {
    const [enhancement, setEnhancement] = useState<TruthfulEnhancement | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const enhance = useCallback(async (content: string, role?: string) => {
        setIsLoading(true)
        setError(null)
        try {
            const result = await resumeApi.enhanceTruthfully(content, role)
            // Map API response to our UI interface if names differ, 
            // but my Pydantic model uses snake_case and my interface currently uses camelCase in standard TS/React.
            // Let's check the API response key names.
            // The Python Pydantic model `TruthfulEnhancement` uses snake_case.
            // The interface `TruthfulEnhancement` in modal uses camelCase.
            // I need to map it here.

            const mappedEnhancement: TruthfulEnhancement = {
                originalText: result.original_text,
                enhancedText: result.enhanced_text,
                requiresVerification: result.requires_user_verification || false,
                verificationPrompt: result.verification_question || result.verification_prompt,
                metricsArePlaceholder: result.metrics_are_placeholder || false,
                groundingExplanation: result.grounding_explanation || result.truthfulness_explanation,
                enhancementType: result.enhancement_type
            }

            setEnhancement(mappedEnhancement)
            return mappedEnhancement
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate enhancement")
            return null
        } finally {
            setIsLoading(false)
        }
    }, [])

    const clearEnhancement = () => setEnhancement(null)

    return {
        enhancement,
        isLoading,
        error,
        enhance,
        clearEnhancement
    }
}
