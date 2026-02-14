import { redirect } from 'next/navigation'
import { getSession } from '@/lib/session'
import Link from 'next/link'
import { BarChart3, Users, Shield, Cpu, ArrowLeft, Rocket } from 'lucide-react'

const adminNavItems = [
    { href: "/admin", label: "Overview", icon: BarChart3 },
    { href: "/admin/users", label: "Users", icon: Users },
    { href: "/admin/governance", label: "Governance", icon: Shield },
]

export default async function AdminLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const session = await getSession()

    if (!session) {
        redirect('/auth/login')
    }

    // Check admin role
    const isAdmin = session.user.roles?.includes('admin') ?? false
    if (!isAdmin) {
        redirect('/dashboard')
    }

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Admin Sidebar — dark theme for visual separation */}
            <aside className="w-64 bg-pencil-black text-white flex flex-col">
                <div className="p-6 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 wobble bg-marker-red flex items-center justify-center">
                            <Shield className="w-6 h-6 text-white" strokeWidth={2.5} />
                        </div>
                        <div>
                            <h1 className="text-xl font-marker text-white">Admin Panel</h1>
                            <p className="text-xs text-white/40 font-handwritten">StellarApply</p>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 py-6 px-4 space-y-1">
                    {adminNavItems.map((link) => {
                        const Icon = link.icon
                        return (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="flex items-center gap-3 px-4 py-3 text-lg font-handwritten text-white/70 hover:bg-white/10 hover:text-white border-2 border-transparent hover:border-white/20 wobble transition-all group rounded-sm"
                            >
                                <Icon className="w-5 h-5 group-hover:rotate-6 transition-transform" strokeWidth={2} />
                                {link.label}
                            </Link>
                        )
                    })}
                </nav>

                <div className="p-4 border-t border-white/10">
                    <Link
                        href="/dashboard"
                        className="flex items-center gap-2 px-4 py-2 text-lg font-handwritten text-white/50 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to Dashboard
                    </Link>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-14 bg-pencil-black/5 border-b-2 border-pencil-black/10 flex items-center px-6">
                    <span className="font-marker text-lg text-pencil-black/60">
                        <Shield className="w-4 h-4 inline mr-2 text-marker-red" />
                        Administrator Mode
                    </span>
                </header>
                <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
                    {children}
                </main>
            </div>
        </div>
    )
}
