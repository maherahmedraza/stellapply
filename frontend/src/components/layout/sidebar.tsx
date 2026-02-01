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
            </nav>

            <div className="p-4 border-t-2 border-dashed border-pencil-black/20">
                <p className="text-sm font-handwritten text-pencil-black/40 text-center">
                    © 2026 StellarApply.ai
                </p>
            </div>
        </aside>
    )
}
