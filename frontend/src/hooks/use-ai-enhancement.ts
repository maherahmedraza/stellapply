import { useState, useCallback } from 'react'
import { resumeApi, EnhancementSuggestion, EnhancementRequest } from '@/lib/api/resume'

export type { EnhancementSuggestion as AISuggestion }

export function useAIEnhancement(sectionId?: string) {
    const [suggestions, setSuggestions] = useState<EnhancementSuggestion[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [appliedSuggestions, setAppliedSuggestions] = useState<number[]>([])

    const fetchEnhancements = useCallback(async (content: string, type: "bullet_point" | "summary" | "description" = "bullet_point") => {
        setIsLoading(true)
        setError(null)
        try {
            const results = await resumeApi.getGroundedEnhancements({
                original_content: content,
                content_type: type
            })
            setSuggestions(results)
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate enhancements")
        } finally {
            setIsLoading(false)
        }
    }, [])

    const regenerate = async (content: string, type: "bullet_point" | "summary" | "description" = "bullet_point") => {
        await fetchEnhancements(content, type)
    }

    const markAsApplied = (index: number) => {
        setAppliedSuggestions(prev => [...prev, index])
    }

    const clearSuggestions = useCallback(() => {
        setSuggestions([])
        setAppliedSuggestions([])
        setError(null)
    }, [])

    return {
        suggestions,
        isLoading,
        error,
        fetchEnhancements,
        regenerate,
        appliedSuggestions,
        markAsApplied,
        setSuggestions,
        clearSuggestions
    }
}
