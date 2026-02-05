import Link from 'next/link'
import { Home, Briefcase, FileText, Send, Settings, Rocket } from 'lucide-react'

interface User {
    name?: string | null
    email?: string | null
    image?: string | null
}

const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: Home },
    { href: "/dashboard/jobs", label: "Job Search", icon: Briefcase },
    { href: "/dashboard/resumes", label: "My Resumes", icon: FileText },
    { href: "/dashboard/applications", label: "Applications", icon: Send },
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
]

export function Sidebar({ user }: { user: User }) {
    void user
    return (
<<<<<<< HEAD
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
=======
        <aside className="w-64 bg-white border-r-3 border-pencil-black flex flex-col">
            <div className="p-6 border-b-2 border-dashed border-pencil-black/20">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="w-10 h-10 wobble bg-marker-red flex items-center justify-center group-hover:rotate-12 transition-transform">
                        <Rocket className="w-6 h-6 text-white" strokeWidth={2.5} />
                    </div>
                    <h1 className="text-2xl font-marker text-pencil-black group-hover:text-ink-blue transition-colors">
                        StellarApply
                    </h1>
                </Link>
            </div>

            <nav className="flex-1 py-6 px-4 space-y-2">
                {navItems.map((link) => {
                    const Icon = link.icon
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className="flex items-center gap-3 px-4 py-3 text-xl font-handwritten text-pencil-black hover:bg-ink-blue hover:text-white border-2 border-transparent hover:border-pencil-black wobble transition-all group"
                        >
                            <Icon className="w-5 h-5 group-hover:rotate-6 transition-transform" strokeWidth={2.5} />
                            {link.label}
                        </Link>
                    )
                })}
>>>>>>> feature/resume-upload-gdpr-compliance
            </nav>

            <div className="p-4 border-t-2 border-dashed border-pencil-black/20">
                <p className="text-sm font-handwritten text-pencil-black/40 text-center">
                    © 2026 StellarApply.ai
                </p>
            </div>
        </aside>
    )
}
