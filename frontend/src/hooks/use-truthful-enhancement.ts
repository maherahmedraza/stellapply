import { useState, useCallback } from 'react'
import { fetcher } from '@/lib/api'

export interface TruthfulEnhancement {
    originalText: string
    enhancedText: string
    verificationStatus: 'verified' | 'plausible' | 'needs_confirmation' | 'rejected'
    confidenceScore: number
    sourcePersonaFields: string[]
    defensibilityScore: number
    interviewTalkingPoints: string[]
    enhancementType: string
    requiresConfirmation: boolean
    confirmationPrompt?: string
}

export function useTruthfulEnhancement() {
    const [enhancement, setEnhancement] = useState<TruthfulEnhancement | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const enhance = useCallback(async (
        originalText: string,
        sectionType: 'summary' | 'bullet_point' | 'description' = 'bullet_point'
    ) => {
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetcher('/api/v1/resume/enhance-truthful', {
                method: 'POST',
                body: JSON.stringify({
                    original_text: originalText,
                    section_type: sectionType
                })
            })

            const data: TruthfulEnhancement = {
                originalText: response.original_text,
                enhancedText: response.enhanced_text,
                verificationStatus: response.verification_status,
                confidenceScore: response.confidence_score,
                sourcePersonaFields: response.source_persona_fields,
                defensibilityScore: response.defensibility_score,
                interviewTalkingPoints: response.interview_talking_points,
                enhancementType: response.enhancement_type,
                requiresConfirmation: response.requires_confirmation,
                confirmationPrompt: response.confirmation_prompt
            }

            setEnhancement(data)
            return data

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate truthful enhancement')
            throw err
        } finally {
            setIsLoading(false)
        }
    }, [])

    const confirmPlaceholders = useCallback(async (
        enhancementId: string,
        placeholderValues: Record<string, string>
    ) => {
        setIsLoading(true)
        try {
            const response = await fetcher('/api/v1/resume/confirm-enhancement', {
                method: 'POST',
                body: JSON.stringify({
                    enhancement_id: enhancementId,
                    placeholder_values: placeholderValues
                })
            })

            setEnhancement(prev => prev ? {
                ...prev,
                enhancedText: response.final_text,
                verificationStatus: 'verified',
                requiresConfirmation: false
            } : null)

            return response.final_text
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to confirm enhancement')
            throw err
        } finally {
            setIsLoading(false)
        }
    }, [])

    return {
        enhance,
        confirmPlaceholders,
        enhancement,
        isLoading,
        error,
        clearEnhancement: () => setEnhancement(null)
    }
}
