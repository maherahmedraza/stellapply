import { redirect } from 'next/navigation'
import { getSession } from '@/lib/session'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
// import { Toaster } from '@/components/ui/toaster' // Commenting out as Toaster might not exist yet

export default async function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const session = await getSession()

    if (!session) {
        redirect('/auth/login')
    }

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar user={session.user} />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Header user={session.user} />
                <main className="flex-1 overflow-y-auto bg-paper-bg p-6">
                    {children}
                </main>
            </div>
            {/* <Toaster /> */}
        </div>
    )
}
