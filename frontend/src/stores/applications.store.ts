import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { apiClient } from '@/lib/api'

type ApplicationStatus =
    | 'queued'
    | 'applied'
    | 'viewed'
    | 'interviewing'
    | 'offered'
    | 'rejected'
    | 'withdrawn'

interface Application {
    id: string
    jobId: string
    job: {
        title: string
        company: string
    }
    status: ApplicationStatus
    appliedAt: string
    resumeId: string
    coverLetterId: string
    notes: string
}

interface QueueItem {
    id: string
    jobId: string
    job: {
        title: string
        company: string
    }
    status: 'pending' | 'scheduled' | 'in_progress' | 'paused'
    scheduledTime: string
    priority: number
}

interface ApplicationsState {
    applications: Application[]
    queue: QueueItem[]
    stats: {
        total: number
        byStatus: Record<ApplicationStatus, number>
        responseRate: number
        interviewRate: number
    }

    isLoading: boolean
    isPaused: boolean

    // Actions
    fetchApplications: () => Promise<void>
    fetchQueue: () => Promise<void>
    updateStatus: (id: string, status: ApplicationStatus) => Promise<void>
    addToQueue: (jobId: string, resumeId: string, coverLetterId: string) => Promise<void>
    removeFromQueue: (id: string) => Promise<void>
    pauseAutomation: () => Promise<void>
    resumeAutomation: () => Promise<void>
}

export const useApplicationsStore = create<ApplicationsState>()(
    immer((set) => ({
        applications: [],
        queue: [],
        stats: {
            total: 0,
            byStatus: {} as Record<ApplicationStatus, number>,
            responseRate: 0,
            interviewRate: 0,
        },

        isLoading: false,
        isPaused: false,

        fetchApplications: async () => {
            set((state) => { state.isLoading = true })

            const response = await apiClient.get('/applications')
            set((state) => {
                state.applications = response.applications || []
                state.stats = response.stats || state.stats
                state.isLoading = false
            })
        },

        fetchQueue: async () => {
            set((state) => { state.isLoading = true })
            const response = await apiClient.get('/applications/queue')
            set((state) => {
                state.queue = response.queue || []
                state.isLoading = false
            })
        },

        updateStatus: async (id, status) => {
            const response = await apiClient.put(`/applications/${id}/status`, { status })
            set((state) => {
                const index = state.applications.findIndex(a => a.id === id)
                if (index !== -1) {
                    state.applications[index] = response
                }
            })
        },

        addToQueue: async (jobId, resumeId, coverLetterId) => {
            const response = await apiClient.post('/applications/queue', { jobId, resumeId, coverLetterId })
            set((state) => {
                state.queue.push(response)
            })
        },

        removeFromQueue: async (id) => {
            await apiClient.delete(`/applications/queue/${id}`)
            set((state) => {
                state.queue = state.queue.filter(item => item.id !== id)
            })
        },

        pauseAutomation: async () => {
            await apiClient.post('/automation/pause', {})
            set((state) => { state.isPaused = true })
        },

        resumeAutomation: async () => {
            await apiClient.post('/automation/resume', {})
            set((state) => { state.isPaused = false })
        }

    }))
)
