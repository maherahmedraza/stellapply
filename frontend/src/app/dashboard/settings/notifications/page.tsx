<<<<<<< HEAD
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
=======
"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Bell, Mail, Smartphone, Clock, BellOff } from "lucide-react";
import Link from "next/link";

interface NotificationSetting {
  id: string;
  label: string;
  description: string;
  email: boolean;
  push: boolean;
}

export default function NotificationsPage() {
  const [settings, setSettings] = useState<NotificationSetting[]>([
    {
      id: "new_matches",
      label: "New Job Matches",
      description: "Get notified when AI finds jobs matching your persona",
      email: true,
      push: true,
    },
    {
      id: "application_status",
      label: "Application Updates",
      description: "Status changes on your submitted applications",
      email: true,
      push: true,
    },
    {
      id: "auto_apply",
      label: "Auto-Apply Results",
      description: "Notifications when auto-apply completes or fails",
      email: true,
      push: false,
    },
    {
      id: "weekly_digest",
      label: "Weekly Digest",
      description: "Summary of your job search activity",
      email: true,
      push: false,
    },
    {
      id: "tips",
      label: "Tips & Insights",
      description: "Career tips and job market insights",
      email: false,
      push: false,
    },
  ]);

  const [digestFrequency, setDigestFrequency] = useState("weekly");

  const toggleSetting = (id: string, type: "email" | "push") => {
    setSettings(settings.map(s =>
      s.id === id ? { ...s, [type]: !s[type] } : s
    ));
  };

  const handleSave = async () => {
    // TODO: API call
    alert("Notification preferences saved! (Mock)");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Notifications</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Control how we keep you in the loop.
        </p>
      </header>

      {/* Quick Toggle */}
      <SketchCard decoration="tape" className="p-6 bg-postit-yellow">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <BellOff className="w-8 h-8 text-pencil-black" />
            <div>
              <h2 className="text-2xl font-marker">Do Not Disturb</h2>
              <p className="font-handwritten text-pencil-black/70">Pause all notifications</p>
            </div>
          </div>
          <button className="px-6 py-3 border-2 border-pencil-black wobble bg-white font-handwritten text-lg hover:bg-pencil-black hover:text-white transition-all">
            Enable DND
          </button>
        </div>
      </SketchCard>

      {/* Notification Settings */}
      <div className="space-y-4">
        <div className="flex justify-end gap-8 px-4 font-marker text-lg">
          <span className="flex items-center gap-2"><Mail className="w-5 h-5" /> Email</span>
          <span className="flex items-center gap-2"><Smartphone className="w-5 h-5" /> Push</span>
        </div>

        {settings.map((setting) => (
          <SketchCard key={setting.id} decoration="none" className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1">
                <Bell className="w-6 h-6 text-ink-blue" />
                <div>
                  <h3 className="text-xl font-marker">{setting.label}</h3>
                  <p className="font-handwritten text-pencil-black/60">{setting.description}</p>
                </div>
              </div>
              <div className="flex gap-8">
                <button
                  onClick={() => toggleSetting(setting.id, "email")}
                  className={`w-12 h-12 border-2 border-pencil-black wobble flex items-center justify-center transition-all ${setting.email ? "bg-ink-blue text-white" : "bg-white"
                    }`}
                >
                  {setting.email ? "✓" : ""}
                </button>
                <button
                  onClick={() => toggleSetting(setting.id, "push")}
                  className={`w-12 h-12 border-2 border-pencil-black wobble flex items-center justify-center transition-all ${setting.push ? "bg-ink-blue text-white" : "bg-white"
                    }`}
                >
                  {setting.push ? "✓" : ""}
                </button>
              </div>
            </div>
          </SketchCard>
        ))}
      </div>

      {/* Digest Frequency */}
      <SketchCard decoration="none" className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-marker-red/10 rounded-full">
            <Clock className="w-6 h-6 text-marker-red" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-marker mb-4">Digest Frequency</h2>
            <div className="flex gap-4">
              {["daily", "weekly", "monthly", "never"].map((freq) => (
                <button
                  key={freq}
                  onClick={() => setDigestFrequency(freq)}
                  className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten text-lg capitalize transition-all ${digestFrequency === freq
                      ? "bg-marker-red text-white"
                      : "bg-white hover:bg-marker-red/10"
                    }`}
                >
                  {freq}
                </button>
              ))}
            </div>
          </div>
        </div>
      </SketchCard>

      <div className="flex justify-end">
        <SketchButton onClick={handleSave} variant="primary" className="text-xl px-8">
          Save Notifications
        </SketchButton>
      </div>
    </div>
  );
>>>>>>> feature/resume-upload-gdpr-compliance
}
