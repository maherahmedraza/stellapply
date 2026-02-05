'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Settings, Save, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { SketchButton } from "@/components/ui/hand-drawn"
import { getUserSettings, updateUserSettings, type UserSettings } from '@/lib/api/persona'

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState<UserSettings>({
    theme: 'system',
    language: 'en',
    timezone: 'Europe/Berlin',
    date_format: 'DD/MM/YYYY',
    job_alerts: true,
    weekly_digest: true,
    match_threshold: 70,
    auto_apply_enabled: false,
    preferred_work_type: 'hybrid',
    salary_visible: false,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const settings = await getUserSettings()
      if (settings) {
        setPreferences(settings)
      }
    } catch (err) {
      console.error('Error loading settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      await updateUserSettings(preferences)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-3xl mx-auto">
        <Link href="/dashboard/settings" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
            <Settings className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold dark:text-white">Preferences</h1>
            <p className="text-gray-600 dark:text-gray-400">Customize your job search experience</p>
          </div>
        </div>

        {saved && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
            ✓ Preferences saved successfully!
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
            ⚠️ {error}
          </div>
        )}

        {/* Display Preferences */}
        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="dark:text-white">Display Settings</CardTitle>
            <CardDescription className="dark:text-gray-400">Customize how the app looks and feels</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Theme</label>
                <select
                  value={preferences.theme}
                  onChange={(e) => setPreferences({ ...preferences, theme: e.target.value })}
                  className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System Default</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Language</label>
                <select
                  value={preferences.language}
                  onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                  className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                  <option value="fr">Français</option>
                  <option value="es">Español</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                  className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="Europe/Berlin">Europe/Berlin (CET)</option>
                  <option value="Europe/London">Europe/London (GMT)</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                  <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
                  <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date Format</label>
                <select
                  value={preferences.date_format}
                  onChange={(e) => setPreferences({ ...preferences, date_format: e.target.value })}
                  className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Job Search Preferences */}
        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="dark:text-white">Job Search Settings</CardTitle>
            <CardDescription className="dark:text-gray-400">Configure your job matching preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Match Threshold: {preferences.match_threshold}%
              </label>
              <input
                type="range"
                min="50"
                max="100"
                value={preferences.match_threshold}
                onChange={(e) => setPreferences({ ...preferences, match_threshold: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg cursor-pointer"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Only show jobs with match score above this threshold
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Preferred Work Type</label>
              <div className="flex gap-4">
                {['onsite', 'hybrid', 'remote'].map((type) => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="workType"
                      value={type}
                      checked={preferences.preferred_work_type === type}
                      onChange={(e) => setPreferences({ ...preferences, preferred_work_type: e.target.value })}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.salary_visible}
                onChange={(e) => setPreferences({ ...preferences, salary_visible: e.target.checked })}
                className="w-5 h-5 rounded"
              />
              <div>
                <span className="text-gray-700 dark:text-gray-300 font-medium">Show Salary Expectations</span>
                <p className="text-xs text-gray-500 dark:text-gray-400">Allow recruiters to see your salary range</p>
              </div>
            </label>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <SketchButton onClick={handleSave} variant="primary" disabled={saving} className="flex items-center gap-2">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {saving ? 'Saving...' : 'Save Preferences'}
          </SketchButton>
        </div>
      </div>
    </div>
  )
}
