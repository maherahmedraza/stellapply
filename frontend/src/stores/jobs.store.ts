import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { apiClient } from '@/lib/api'

interface Job {
    id: string
    title: string
    company: {
        name: string
        logo?: string
        size?: string
    }
    location: string
    salary?: {
        min: number
        max: number
    }
    isRemote: boolean
    matchScore: number
    postedDate: string
    applyUrl: string
}

interface JobsState {
    jobs: Job[]
    matches: Job[]
    savedJobs: Job[]
    currentJob: Job | null

    filters: {
        keywords: string[]
        location: string
        remoteOnly: boolean
        salaryMin: number | null
        experienceLevel: string | null
    }

    pagination: {
        page: number
        totalPages: number
        totalJobs: number
    }

    isLoading: boolean

    // Actions
    searchJobs: (filters?: Partial<JobsState['filters']>) => Promise<void>
    fetchMatches: () => Promise<void>
    saveJob: (jobId: string) => Promise<void>
    unsaveJob: (jobId: string) => Promise<void>
    skipJob: (jobId: string) => Promise<void>
    setFilters: (filters: Partial<JobsState['filters']>) => void
    setCurrentJob: (job: Job | null) => void
}

export const useJobsStore = create<JobsState>()(
    immer((set, get) => ({
        jobs: [],
        matches: [],
        savedJobs: [],
        currentJob: null,

        filters: {
            keywords: [],
            location: '',
            remoteOnly: false,
            salaryMin: null,
            experienceLevel: null,
        },

        pagination: {
            page: 1,
            totalPages: 1,
            totalJobs: 0,
        },

        isLoading: false,

        searchJobs: async (newFilters) => {
            const filters = { ...get().filters, ...newFilters }
            set((state) => {
                state.filters = filters
                state.isLoading = true
            })

            try {
                const response = await apiClient.get('/jobs', {
                    headers: {
                        // params sent as headers or handled by fetcher modification usually
                    }
                })
                // Mocking response structure access since apiClient returns json directly
                set((state) => {
                    state.jobs = response.jobs || []
                    state.pagination = response.pagination || state.pagination
                    state.isLoading = false
                })
            } catch {
                set((state) => { state.isLoading = false })
            }
        },

        fetchMatches: async () => {
            set((state) => { state.isLoading = true })

            try {
                const response = await apiClient.get('/jobs/matches')
                set((state) => {
                    state.matches = response.matches || []
                    state.isLoading = false
                })
            } catch {
                set((state) => { state.isLoading = false })
            }
        },

        saveJob: async (jobId) => {
            await apiClient.post(`/jobs/${jobId}/save`, {})
            const job = get().jobs.find(j => j.id === jobId)
            if (job) {
                set((state) => {
                    state.savedJobs.push(job)
                })
            }
        },

        unsaveJob: async (jobId) => {
            await apiClient.delete(`/jobs/${jobId}/save`)
            set((state) => {
                state.savedJobs = state.savedJobs.filter(j => j.id !== jobId)
            })
        },

        skipJob: async (jobId) => {
            // Logic to remove job from view
            await apiClient.post(`/jobs/${jobId}/skip`, {})
            set((state) => {
                state.jobs = state.jobs.filter(j => j.id !== jobId)
            })
        },

        setFilters: (filters) => {
            set((state) => {
                Object.assign(state.filters, filters)
            })
        },

        setCurrentJob: (job) => {
            set((state) => {
                state.currentJob = job
            })
        }

    }))
)
