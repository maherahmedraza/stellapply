import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { arrayMove } from '@dnd-kit/sortable'
import { api } from '@/lib/api'

// ============================================
// Type Definitions
// ============================================

export interface ExperienceContent {
    id: string
    company: string
    title: string
    startDate: string
    endDate?: string
    description: string
    achievements: string[]
    // Original vs Enhanced tracking
    description_original?: string
    description_enhanced?: string
    bullets_original?: string[]
    bullets_enhanced?: string[]
}

export interface EducationContent {
    id: string
    school: string
    degree: string
    field?: string
    year: string
    gpa?: number
}

export interface SkillContent {
    name: string
    category?: string
    proficiency?: number
}

// Union type for section content
export type SectionContent =
    | string                    // Summary
    | ExperienceContent[]       // Experience
    | EducationContent[]        // Education
    | SkillContent[] | string[] // Skills (can be objects or simple strings)
    | unknown                   // Custom sections

export interface ResumeSection {
    id: string
    title: string
    type: 'summary' | 'experience' | 'education' | 'skills' | 'custom'
    content: SectionContent
    isVisible: boolean
    order?: number
}

export interface ResumeData {
    id: string
    title: string
    templateId: string
    personaId?: string
    sections: ResumeSection[]
    atsScore?: number
    lastModified?: string
}

interface ATSAnalysis {
    score: number
    breakdown: {
        format: number
        content: number
        keywords: number
        bestPractices: number
    }
    issues: Array<{
        severity: 'critical' | 'major' | 'minor'
        message: string
        suggestion: string
    }>
}

// ============================================
// Store State Interface
// ============================================

interface ResumeState {
    // State
    resume: ResumeData | null
    sections: ResumeSection[]
    atsScore: number
    atsAnalysis: ATSAnalysis | null
    isLoading: boolean
    isEnhancing: boolean
    isSaving: boolean
    error: string | null

    // Actions
    setResume: (resume: ResumeData) => void
    loadResume: (resumeId: string) => Promise<void>
    saveResume: () => Promise<void>
    updateSection: (sectionId: string, data: Partial<ResumeSection>) => void
    updateSectionContent: <T extends SectionContent>(sectionId: string, content: T) => void
    reorderSections: (activeId: string, overId: string) => void
    toggleSectionVisibility: (sectionId: string) => void
    enhanceWithAI: (sectionId: string) => Promise<void>
    analyzeATS: () => Promise<void>
    downloadResume: (format: 'pdf' | 'docx') => Promise<void>
    updateResume: (updates: Partial<ResumeData>) => void
    clearError: () => void
}

// ============================================
// Initial Data
// ============================================

const createInitialSections = (): ResumeSection[] => [
    {
        id: 'summary',
        title: 'Professional Summary',
        type: 'summary',
        content: '',
        isVisible: true,
        order: 0
    },
    {
        id: 'experience',
        title: 'Work Experience',
        type: 'experience',
        content: [] as ExperienceContent[],
        isVisible: true,
        order: 1
    },
    {
        id: 'education',
        title: 'Education',
        type: 'education',
        content: [] as EducationContent[],
        isVisible: true,
        order: 2
    },
    {
        id: 'skills',
        title: 'Skills',
        type: 'skills',
        content: [] as string[],
        isVisible: true,
        order: 3
    },
]

// ============================================
// API Response Mappers
// ============================================

interface APIExperience {
    id: string
    company_name: string
    job_title: string
    start_date: string
    end_date?: string
    description?: string
    bullets?: string[]
    description_active?: string
    description_original?: string
    description_enhanced?: string
    bullets_active?: string[]
    bullets_original?: string[]
    bullets_enhanced?: string[]
}

interface APIEducation {
    id: string
    institution_name: string
    degree_type: string
    field_of_study?: string
    graduation_date?: string
    gpa?: number
}

interface APISkill {
    id: string
    name: string
    category?: string
    proficiency_level?: number
}

interface APIRenderedResume {
    summary?: string
    experiences?: APIExperience[]
    education?: APIEducation[]
    skills?: APISkill[]
}

function mapAPIExperienceToContent(exp: APIExperience): ExperienceContent {
    return {
        id: exp.id,
        company: exp.company_name,
        title: exp.job_title,
        startDate: exp.start_date,
        endDate: exp.end_date,
        description: exp.description || exp.description_active || exp.description_original || '',
        achievements: exp.bullets || exp.bullets_active || exp.bullets_original || [],
        description_original: exp.description_original,
        description_enhanced: exp.description_enhanced,
        bullets_original: exp.bullets_original,
        bullets_enhanced: exp.bullets_enhanced,
    }
}

function mapAPIEducationToContent(edu: APIEducation): EducationContent {
    return {
        id: edu.id,
        school: edu.institution_name,
        degree: edu.degree_type,
        field: edu.field_of_study,
        year: edu.graduation_date || '',
        gpa: edu.gpa,
    }
}

function mapRenderedDataToSections(
    renderedData: APIRenderedResume,
    baseSections: ResumeSection[]
): ResumeSection[] {
    return baseSections.map(section => {
        switch (section.type) {
            case 'summary':
                return { ...section, content: renderedData.summary || '' }

            case 'experience':
                return {
                    ...section,
                    content: renderedData.experiences?.map(mapAPIExperienceToContent) || []
                }

            case 'education':
                return {
                    ...section,
                    content: renderedData.education?.map(mapAPIEducationToContent) || []
                }

            case 'skills':
                return {
                    ...section,
                    content: renderedData.skills?.map(s => s.name) || []
                }

            default:
                return section
        }
    })
}

// ============================================
// Store Implementation
// ============================================

export const useResumeStore = create<ResumeState>()(
    immer((set, get) => ({
        // Initial State
        resume: null,
        sections: createInitialSections(),
        atsScore: 0,
        atsAnalysis: null,
        isLoading: false,
        isEnhancing: false,
        isSaving: false,
        error: null,

        // Actions
        setResume: (resume) => set((state) => {
            state.resume = resume
            state.sections = resume.sections
        }),

        loadResume: async (resumeId: string) => {
            set((state) => {
                state.isLoading = true
                state.error = null
            })

            try {
                // Fetch resume metadata
                const resumeData = await api.get(`/api/v1/resume/${resumeId}`)

                // Fetch rendered content from Persona
                const renderedData: APIRenderedResume = await api.get(
                    `/api/v1/resume/${resumeId}/render`
                )

                // Map to sections
                const populatedSections = mapRenderedDataToSections(
                    renderedData,
                    createInitialSections()
                )

                set((state) => {
                    state.resume = {
                        id: resumeData.id,
                        title: resumeData.name,
                        templateId: resumeData.template_id || 'modern',
                        personaId: resumeData.persona_id,
                        sections: populatedSections,
                        atsScore: resumeData.ats_score,
                        lastModified: resumeData.updated_at,
                    }
                    state.sections = populatedSections
                    state.atsScore = resumeData.ats_score || 0
                    state.isLoading = false
                })

            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to load resume'
                set((state) => {
                    state.error = message
                    state.isLoading = false
                })
                throw error
            }
        },

        saveResume: async () => {
            const { resume, sections } = get()
            if (!resume) return

            set((state) => { state.isSaving = true })

            try {
                await api.put(`/api/v1/resume/${resume.id}`, {
                    name: resume.title,
                    template_id: resume.templateId,
                    content_selection: {
                        // Map sections back to content selection format
                        experiences: sections
                            .find(s => s.type === 'experience')
                            ?.content as ExperienceContent[] || [],
                    }
                })

                set((state) => { state.isSaving = false })
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to save resume'
                set((state) => {
                    state.error = message
                    state.isSaving = false
                })
                throw error
            }
        },

        updateSection: (sectionId, data) => set((state) => {
            const index = state.sections.findIndex(s => s.id === sectionId)
            if (index !== -1) {
                state.sections[index] = { ...state.sections[index], ...data }
            }
        }),

        updateSectionContent: (sectionId, content) => set((state) => {
            const index = state.sections.findIndex(s => s.id === sectionId)
            if (index !== -1) {
                state.sections[index].content = content
            }
        }),

        reorderSections: (activeId, overId) => set((state) => {
            const oldIndex = state.sections.findIndex(s => s.id === activeId)
            const newIndex = state.sections.findIndex(s => s.id === overId)
            if (oldIndex !== -1 && newIndex !== -1) {
                state.sections = arrayMove(state.sections, oldIndex, newIndex)
            }
        }),

        toggleSectionVisibility: (sectionId) => set((state) => {
            const section = state.sections.find(s => s.id === sectionId)
            if (section) {
                section.isVisible = !section.isVisible
            }
        }),

        enhanceWithAI: async (sectionId) => {
            set((state) => { state.isEnhancing = true })

            try {
                // This would call your AI enhancement API
                await new Promise(resolve => setTimeout(resolve, 2000))
                // Handle response and update section
            } finally {
                set((state) => { state.isEnhancing = false })
            }
        },

        analyzeATS: async () => {
            const { resume, sections } = get()
            if (!resume) return

            try {
                const analysis = await api.post(`/api/v1/resume/${resume.id}/analyze`, {
                    sections: sections.filter(s => s.isVisible)
                })

                set((state) => {
                    state.atsScore = analysis.score
                    state.atsAnalysis = analysis
                })
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to analyze resume'
                set((state) => { state.error = message })
            }
        },

        downloadResume: async (format) => {
            const { resume } = get()
            if (!resume) return

            try {
                // api.getBlob is probably needed, let's assume it exists or use fetch fallback
                const res = await fetch(`/api/v1/resume/${resume.id}/download?format=${format}`);
                const blob = await res.blob();

                // Trigger download
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${resume.title}.${format}`
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to download resume'
                set((state) => { state.error = message })
            }
        },

        updateResume: (updates) => set((state) => {
            if (state.resume) {
                Object.assign(state.resume, updates)
            }
        }),

        clearError: () => set((state) => { state.error = null }),
    }))
)

// ============================================
// Selector Hooks for Performance
// ============================================

export const useResumeSection = (sectionId: string) =>
    useResumeStore((state) => state.sections.find(s => s.id === sectionId))

export const useResumeSections = () =>
    useResumeStore((state) => state.sections)

export const useResumeATSScore = () =>
    useResumeStore((state) => state.atsScore)

export const useResumeIsLoading = () =>
    useResumeStore((state) => state.isLoading)
