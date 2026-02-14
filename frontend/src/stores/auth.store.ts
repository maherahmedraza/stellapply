import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

interface User {
    id: string
    email: string
    fullName: string
    tier: 'free' | 'plus' | 'pro' | 'premium'
    avatarUrl?: string
}

interface AuthState {
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    setUser: (user: User) => void
    setTokens: (accessToken: string, refreshToken: string) => void
    logout: () => void
    refreshAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
    persist(
        immer((set, get) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: true,

            setUser: (user) => set((state) => {
                state.user = user
                state.isAuthenticated = true
                state.isLoading = false
            }),

            setTokens: (accessToken, refreshToken) => set((state) => {
                state.accessToken = accessToken
                state.refreshToken = refreshToken
            }),

            logout: () => {
                // Clear state
                set((state) => {
                    state.user = null
                    state.accessToken = null
                    state.refreshToken = null
                    state.isAuthenticated = false
                })

                // Clear cookies
                document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT"

                // Redirect to login
                window.location.href = "/auth/login"
            },

            refreshAuth: async () => {
                const { refreshToken } = get()
                if (!refreshToken) {
                    get().logout()
                    return
                }

                try {
                    const response = await fetch('/api/auth/refresh', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ refresh_token: refreshToken }),
                    })

                    if (!response.ok) throw new Error('Refresh failed')

                    const data = await response.json()
                    set((state) => {
                        state.accessToken = data.access_token
                        state.refreshToken = data.refresh_token
                    })
                } catch {
                    get().logout()
                }
            },
        })),
        {
            name: 'auth-storage',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                user: state.user,
                isAuthenticated: state.isAuthenticated,
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
            onRehydrateStorage: () => (state) => {
                // After hydration from localStorage, mark loading as done
                if (state) {
                    state.isLoading = false
                }
            },
        }
    )
)
