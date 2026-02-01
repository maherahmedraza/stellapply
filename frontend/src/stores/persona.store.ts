import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { apiClient } from '@/lib/api'

interface Experience {
    id: string
    company: string
    title: string
    startDate: string
    endDate?: string
    description: string
    achievements: string[]
}

interface Skill {
    id: string
    name: string
    category: 'technical' | 'soft' | 'tool' | 'language'
    proficiency: number
}

interface PersonaState {
    persona: {
        id: string
        fullName: string
        email: string
        phone: string
        location: {
            city: string
            state: string
            country: string
        }
        experiences: Experience[]
        skills: Skill[]
        completenessScore: number
    } | null
    isLoading: boolean
    error: string | null

    // Actions
    fetchPersona: () => Promise<void>
    updatePersona: (updates: Partial<PersonaState['persona']>) => Promise<void>
    addExperience: (experience: Omit<Experience, 'id'>) => Promise<void>
    updateExperience: (id: string, updates: Partial<Experience>) => Promise<void>
    deleteExperience: (id: string) => Promise<void>
    addSkill: (skill: Omit<Skill, 'id'>) => Promise<void>
    removeSkill: (id: string) => Promise<void>
}

export const usePersonaStore = create<PersonaState>()(
    immer((set) => ({
        persona: null,
        isLoading: false,
        error: null,

        fetchPersona: async () => {
            set((state) => { state.isLoading = true })

            try {
                const response = await apiClient.get('/persona')
                set((state) => {
                    state.persona = response
                    state.isLoading = false
                })
            } catch {
                set((state) => {
                    state.error = 'Failed to load persona'
                    state.isLoading = false
                })
            }
        },

        updatePersona: async (updates) => {
            try {
                const response = await apiClient.put('/persona', updates)
                set((state) => {
                    if (state.persona) {
                        Object.assign(state.persona, response)
                    }
                })
            } catch (error) {
                set((state) => { state.error = 'Failed to update persona' })
                throw error
            }
        },

        addExperience: async (experience) => {
            const response = await apiClient.post('/persona/experiences', experience)
            set((state) => {
                if (state.persona) {
                    state.persona.experiences.push(response)
                }
            })
        },

        updateExperience: async (id, updates) => {
            const response = await apiClient.put(`/persona/experiences/${id}`, updates)
            set((state) => {
                if (state.persona) {
                    const index = state.persona.experiences.findIndex(e => e.id === id)
                    if (index !== -1) {
                        state.persona.experiences[index] = response
                    }
                }
            })
        },

        deleteExperience: async (id) => {
            await apiClient.delete(`/persona/experiences/${id}`)
            set((state) => {
                if (state.persona) {
                    state.persona.experiences = state.persona.experiences.filter(e => e.id !== id)
                }
            })
        },

        addSkill: async (skill) => {
            const response = await apiClient.post('/persona/skills', skill)
            set((state) => {
                if (state.persona) {
                    state.persona.skills.push(response)
                }
            })
        },

        removeSkill: async (id) => {
            await apiClient.delete(`/persona/skills/${id}`)
            set((state) => {
                if (state.persona) {
                    state.persona.skills = state.persona.skills.filter(s => s.id !== id)
                }
            })
        }
    }))
)
