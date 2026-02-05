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
        <aside className="w-64 bg-card-bg border-r-2 border-dashed border-pencil-black/10 transition-colors flex flex-col h-full">
            <div className="p-8">
                <h1 className="text-3xl font-marker text-pencil-black dark:text-white -rotate-2">
                    Stellapply
                </h1>
            </div>
            <nav className="mt-4 px-4 space-y-2 font-handwritten text-xl">
                {[
                    { label: 'Dashboard', href: '/dashboard' },
                    { label: 'My Persona', href: '/dashboard/persona' },
                    { label: 'Job Search', href: '/dashboard/jobs' },
                    { label: 'My Resumes', href: '/dashboard/resumes' },
                    { label: 'Applications', href: '/dashboard/applications' },
                    { label: 'Settings', href: '/dashboard/settings' },
                ].map((item) => (
                    <Link
                        key={item.href}
                        href={item.href}
                        className="flex items-center px-4 py-3 text-pencil-black dark:text-white hover:bg-pencil-black/5 dark:hover:bg-white/5 wobble rounded-none transition-colors"
                    >
                        {item.label}
                    </Link>
                ))}
            </nav>
        </aside>
    )
}
