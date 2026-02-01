import { useState } from 'react'

export interface AISuggestion {
    original: string
    enhanced: string
    metricsAdded: boolean
}

export function useAIEnhancement(sectionId?: string) {
    void sectionId; // Placeholder usage
    const [suggestions, setSuggestions] = useState<AISuggestion[]>([
        {
            original: "Responsible for managing projects",
            enhanced: "Led cross-functional teams of 10+ members to deliver 5 high-priority projects 20% ahead of schedule.",
            metricsAdded: true
        },
        {
            original: "Fixed bugs in the system",
            enhanced: "Diagnosed and resolved 50+ critical production bugs, reducing system downtime by 15%.",
            metricsAdded: true
        }
    ])
    const [isLoading, setIsLoading] = useState(false)
    const [appliedSuggestions, setAppliedSuggestions] = useState<number[]>([])

    const regenerate = async () => {
        setIsLoading(true)
        await new Promise(resolve => setTimeout(resolve, 1500))
        setSuggestions(prev => [
            ...prev,
            {
                original: "New generated suggestion",
                enhanced: "Enhanced version with stronger action verbs and quantifiable results.",
                metricsAdded: false
            }
        ])
        setIsLoading(false)
    }

    const markAsApplied = (index: number) => {
        setAppliedSuggestions(prev => [...prev, index])
    }

    return {
        suggestions,
        isLoading,
        regenerate,
        appliedSuggestions,
        markAsApplied
    }
}
