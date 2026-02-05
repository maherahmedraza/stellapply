'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Bell, Save, Mail, Smartphone, MessageSquare } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { SketchButton } from "@/components/ui/hand-drawn"

interface NotificationSetting {
  id: string
  title: string
  description: string
  email: boolean
  push: boolean
  inApp: boolean
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationSetting[]>([
    {
      id: 'new_matches',
      title: 'New Job Matches',
      description: 'When AI finds jobs matching your profile',
      email: true,
      push: true,
      inApp: true,
    },
    {
      id: 'application_updates',
      title: 'Application Updates',
      description: 'Status changes on your applications',
      email: true,
      push: true,
      inApp: true,
    },
    {
      id: 'weekly_digest',
      title: 'Weekly Digest',
      description: 'Summary of new opportunities each week',
      email: true,
      push: false,
      inApp: false,
    },
    {
      id: 'saved_jobs',
      title: 'Saved Job Updates',
      description: 'Changes to jobs you\'ve saved',
      email: false,
      push: true,
      inApp: true,
    },
    {
      id: 'interview_reminders',
      title: 'Interview Reminders',
      description: 'Upcoming interview notifications',
      email: true,
      push: true,
      inApp: true,
    },
    {
      id: 'tips_resources',
      title: 'Tips & Resources',
      description: 'Career advice and platform updates',
      email: false,
      push: false,
      inApp: true,
    },
  ])
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const updateNotification = (id: string, channel: 'email' | 'push' | 'inApp', value: boolean) => {
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, [channel]: value } : n
    ))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-3xl mx-auto">
        <Link href="/dashboard/settings" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center">
            <Bell className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold dark:text-white">Notifications</h1>
            <p className="text-gray-600 dark:text-gray-400">Configure how you receive updates</p>
          </div>
        </div>

        {saved && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
            ✓ Notification settings saved!
          </div>
        )}

        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="dark:text-white">Notification Channels</CardTitle>
            <CardDescription className="dark:text-gray-400">Choose how you want to be notified</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-2 text-gray-700 dark:text-gray-300 font-medium">Notification Type</th>
                    <th className="text-center py-3 px-2">
                      <div className="flex flex-col items-center gap-1">
                        <Mail className="w-5 h-5 text-gray-500" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">Email</span>
                      </div>
                    </th>
                    <th className="text-center py-3 px-2">
                      <div className="flex flex-col items-center gap-1">
                        <Smartphone className="w-5 h-5 text-gray-500" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">Push</span>
                      </div>
                    </th>
                    <th className="text-center py-3 px-2">
                      <div className="flex flex-col items-center gap-1">
                        <MessageSquare className="w-5 h-5 text-gray-500" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">In-App</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {notifications.map((notif) => (
                    <tr key={notif.id} className="border-b border-gray-100 dark:border-gray-700">
                      <td className="py-4 px-2">
                        <div className="font-medium text-gray-900 dark:text-white">{notif.title}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{notif.description}</div>
                      </td>
                      <td className="text-center py-4 px-2">
                        <input
                          type="checkbox"
                          checked={notif.email}
                          onChange={(e) => updateNotification(notif.id, 'email', e.target.checked)}
                          className="w-5 h-5 rounded cursor-pointer"
                        />
                      </td>
                      <td className="text-center py-4 px-2">
                        <input
                          type="checkbox"
                          checked={notif.push}
                          onChange={(e) => updateNotification(notif.id, 'push', e.target.checked)}
                          className="w-5 h-5 rounded cursor-pointer"
                        />
                      </td>
                      <td className="text-center py-4 px-2">
                        <input
                          type="checkbox"
                          checked={notif.inApp}
                          onChange={(e) => updateNotification(notif.id, 'inApp', e.target.checked)}
                          className="w-5 h-5 rounded cursor-pointer"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="dark:text-white">Quiet Hours</CardTitle>
            <CardDescription className="dark:text-gray-400">Don't disturb me during these times</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">From</label>
                <input type="time" defaultValue="22:00" className="p-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white" />
              </div>
              <span className="text-gray-500 mt-6">to</span>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">To</label>
                <input type="time" defaultValue="08:00" className="p-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <SketchButton onClick={handleSave} variant="primary" disabled={saving} className="flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Notifications'}
          </SketchButton>
        </div>
      </div>
    </div>
  )
}
