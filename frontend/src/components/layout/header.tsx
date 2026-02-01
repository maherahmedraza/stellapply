interface User {
    name?: string | null
    email?: string | null
    image?: string | null
}

export function Header({ user }: { user: User }) {
    return (
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
                {/* Breadcrumbs or Title could go here */}
                <span className="font-semibold text-gray-700 dark:text-gray-200">Welcome, {user?.name || 'User'}</span>
            </div>
            <div className="flex items-center gap-4">
                {/* User Menu / Notifications */}
                <div className="w-8 h-8 rounded-full bg-gray-200" />
            </div>
        </header>
    )
}
