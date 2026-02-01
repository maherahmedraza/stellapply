import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { arrayMove } from '@dnd-kit/sortable'

export interface ResumeSection {
    id: string
    title: string
    type: 'summary' | 'experience' | 'education' | 'skills' | 'custom'
    content: unknown
    isVisible: boolean
}

export interface ResumeData {
    id: string
    title: string
    templateId: string
    sections: ResumeSection[]
}

interface ResumeState {
    resume: ResumeData | null
    sections: ResumeSection[]
    atsScore: number
    isEnhancing: boolean

    // Actions
    setResume: (resume: ResumeData) => void
    updateSection: (sectionId: string, data: Partial<ResumeSection>) => void
    reorderSections: (activeId: string, overId: string) => void
    enhanceWithAI: (sectionId: string) => Promise<void>
    analyzeATS: () => Promise<void>
    downloadResume: (format: 'pdf' | 'docx') => Promise<void>
    updateResume: (updates: Partial<ResumeData>) => void
}

// Mock initial data
const initialSections: ResumeSection[] = [
    { id: 'summary', title: 'Professional Summary', type: 'summary', content: '', isVisible: true },
    { id: 'experience', title: 'Work Experience', type: 'experience', content: [], isVisible: true },
    { id: 'education', title: 'Education', type: 'education', content: [], isVisible: true },
    { id: 'skills', title: 'Skills', type: 'skills', content: [], isVisible: true },
]

export const useResumeStore = create<ResumeState>()(
    immer((set) => ({
        resume: {
            id: 'default',
            title: 'My Resume',
            templateId: 'modern',
            sections: initialSections
        },
        sections: initialSections,
        atsScore: 75,
        isEnhancing: false,

        setResume: (resume) => set((state) => {
            state.resume = resume
            state.sections = resume.sections
        }),

        updateSection: (sectionId, data) => set((state) => {
            const index = state.sections.findIndex(s => s.id === sectionId)
            if (index !== -1) {
                // Handle content update specifically if needed, or generic merge
                state.sections[index] = { ...state.sections[index], ...data }
            }
        }),

        reorderSections: (activeId, overId) => set((state) => {
            const oldIndex = state.sections.findIndex(s => s.id === activeId)
            const newIndex = state.sections.findIndex(s => s.id === overId)
            state.sections = arrayMove(state.sections, oldIndex, newIndex)
        }),

        enhanceWithAI: async (sectionId) => {
            void sectionId; // Mock
            set((state) => { state.isEnhancing = true })
            // Mock API call
            await new Promise(resolve => setTimeout(resolve, 2000))
            set((state) => { state.isEnhancing = false })
        },

        analyzeATS: async () => {
            // Mock analysis
            const newScore = Math.floor(Math.random() * 30) + 70
            set((state) => { state.atsScore = newScore })
        },

        downloadResume: async (format) => {
            console.log(`Downloading as ${format}...`)
            await new Promise(resolve => setTimeout(resolve, 1000))
        },

        updateResume: (updates) => set((state) => {
            if (state.resume) {
                Object.assign(state.resume, updates)
            }
        })
    }))
)
