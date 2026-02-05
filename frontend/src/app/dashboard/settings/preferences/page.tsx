<<<<<<< HEAD
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
=======
"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { MapPin, Briefcase, DollarSign, Building2, Globe } from "lucide-react";
import Link from "next/link";

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState({
    targetRoles: ["Software Engineer", "Data Engineer"],
    locations: ["Remote", "San Francisco", "New York"],
    salaryMin: 120000,
    salaryMax: 180000,
    remotePreference: "remote",
    industries: ["Technology", "Finance", "Healthcare"],
    companySize: ["startup", "medium"],
  });

  const handleSave = async () => {
    // TODO: API call to save preferences
    alert("Preferences saved! (Mock)");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Job Preferences</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Sketch out your ideal job search parameters.
        </p>
      </header>

      <div className="grid gap-6">
        {/* Target Roles */}
        <SketchCard decoration="tape" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-ink-blue/10 rounded-full">
              <Briefcase className="w-6 h-6 text-ink-blue" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Target Roles</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {preferences.targetRoles.map((role, i) => (
                  <span key={i} className="px-3 py-1 bg-ink-blue/10 border-2 border-ink-blue wobble font-handwritten">
                    {role}
                  </span>
                ))}
              </div>
              <input
                type="text"
                placeholder="Add a role..."
                className="w-full p-3 border-2 border-pencil-black wobble bg-white dark:bg-muted-paper font-handwritten"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && e.currentTarget.value) {
                    setPreferences({
                      ...preferences,
                      targetRoles: [...preferences.targetRoles, e.currentTarget.value]
                    });
                    e.currentTarget.value = "";
                  }
                }}
              />
            </div>
          </div>
        </SketchCard>

        {/* Locations */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-marker-red/10 rounded-full">
              <MapPin className="w-6 h-6 text-marker-red" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Preferred Locations</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {preferences.locations.map((loc, i) => (
                  <span key={i} className="px-3 py-1 bg-marker-red/10 border-2 border-marker-red wobble font-handwritten">
                    {loc}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Salary Range */}
        <SketchCard decoration="none" className="p-6 bg-postit-yellow">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-pencil-black/10 rounded-full">
              <DollarSign className="w-6 h-6 text-pencil-black" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Salary Range</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="font-handwritten text-lg block mb-2">Minimum</label>
                  <input
                    type="number"
                    value={preferences.salaryMin}
                    onChange={(e) => setPreferences({ ...preferences, salaryMin: parseInt(e.target.value) })}
                    className="w-full p-3 border-2 border-pencil-black wobble bg-white font-handwritten text-xl"
                  />
                </div>
                <div>
                  <label className="font-handwritten text-lg block mb-2">Maximum</label>
                  <input
                    type="number"
                    value={preferences.salaryMax}
                    onChange={(e) => setPreferences({ ...preferences, salaryMax: parseInt(e.target.value) })}
                    className="w-full p-3 border-2 border-pencil-black wobble bg-white font-handwritten text-xl"
                  />
                </div>
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Remote Preference */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-ink-blue/10 rounded-full">
              <Globe className="w-6 h-6 text-ink-blue" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Work Setting</h2>
              <div className="flex gap-4">
                {["remote", "hybrid", "onsite", "any"].map((option) => (
                  <button
                    key={option}
                    onClick={() => setPreferences({ ...preferences, remotePreference: option })}
                    className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten text-lg capitalize transition-all ${preferences.remotePreference === option
                        ? "bg-ink-blue text-white"
                        : "bg-white hover:bg-ink-blue/10"
                      }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Company Size */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-postit-yellow rounded-full">
              <Building2 className="w-6 h-6 text-pencil-black" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Company Size</h2>
              <div className="flex flex-wrap gap-3">
                {[
                  { id: "startup", label: "Startup (1-50)" },
                  { id: "small", label: "Small (51-200)" },
                  { id: "medium", label: "Medium (201-1000)" },
                  { id: "large", label: "Large (1000+)" },
                  { id: "enterprise", label: "Enterprise (10000+)" },
                ].map((size) => (
                  <button
                    key={size.id}
                    onClick={() => {
                      const current = preferences.companySize;
                      const updated = current.includes(size.id)
                        ? current.filter(s => s !== size.id)
                        : [...current, size.id];
                      setPreferences({ ...preferences, companySize: updated });
                    }}
                    className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten transition-all ${preferences.companySize.includes(size.id)
                        ? "bg-pencil-black text-white"
                        : "bg-white hover:bg-muted-paper"
                      }`}
                  >
                    {size.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>
      </div>

      <div className="flex justify-end">
        <SketchButton onClick={handleSave} variant="primary" className="text-xl px-8">
          Save Preferences
        </SketchButton>
      </div>
    </div>
  );
>>>>>>> feature/resume-upload-gdpr-compliance
}
