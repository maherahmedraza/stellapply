import Link from 'next/link'

interface User {
    name?: string | null
    email?: string | null
    image?: string | null
}

export function Sidebar({ user }: { user: User }) {
    // Use user to silence warning if needed, or remove if truly not needed yet
    void user
    return (
        <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
            <div className="p-6">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    StellarApply
                </h1>
            </div>
            <nav className="mt-6 px-4">
                <Link href="/dashboard" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    Dashboard
                </Link>
                <Link href="/dashboard/jobs" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    Job Search
                </Link>
                <Link href="/dashboard/resumes" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    My Resumes
                </Link>
                <Link href="/dashboard/applications" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    Applications
                </Link>
                <Link href="/dashboard/settings" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    Settings
                </Link>
            </nav>
        </aside>
    )
}
