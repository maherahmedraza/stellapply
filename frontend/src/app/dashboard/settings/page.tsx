'use client'

import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const settingsSections = [
  {
    title: 'Data Control',
    description: 'Manage your data, export, or delete your account',
    href: '/dashboard/settings/data-control',
    icon: '🔒'
  },
  {
    title: 'Preferences',
    description: 'Customize your job search preferences',
    href: '/dashboard/settings/preferences',
    icon: '⚙️'
  },
  {
    title: 'Notifications',
    description: 'Configure email and push notifications',
    href: '/dashboard/settings/notifications',
    icon: '🔔'
  },
  {
    title: 'Automation',
    description: 'Set up auto-apply and job alerts',
    href: '/dashboard/settings/automation',
    icon: '🤖'
  },
  {
    title: 'Billing',
    description: 'Manage your subscription and payment',
    href: '/dashboard/settings/billing',
    icon: '💳'
  }
]

export default function SettingsPage() {
  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Manage your account settings and preferences
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {settingsSections.map((section) => (
            <Link key={section.href} href={section.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{section.icon}</span>
                    <div>
                      <CardTitle className="text-lg dark:text-white">
                        {section.title}
                      </CardTitle>
                      <CardDescription className="dark:text-gray-400">
                        {section.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
