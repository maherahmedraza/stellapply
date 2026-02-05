'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Bot, Save, Zap, Clock, Filter, Play, Pause } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"

export default function AutomationPage() {
  const [automation, setAutomation] = useState({
    autoApplyEnabled: false,
    maxAppsPerDay: 10,
    autoApplySchedule: 'weekdays',
    requiresReview: true,
    excludeCompanies: ['Current Employer, Inc.'],
    jobAlerts: [
      { id: '1', name: 'Senior Data Engineer - Remote', keywords: 'data engineer, remote, python', frequency: 'daily', enabled: true },
      { id: '2', name: 'Tech Lead Roles - Berlin', keywords: 'tech lead, engineering manager, berlin', frequency: 'weekly', enabled: true },
    ]
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [newAlert, setNewAlert] = useState({ name: '', keywords: '', frequency: 'daily' })

  const handleSave = async () => {
    setSaving(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const addAlert = () => {
    if (!newAlert.name || !newAlert.keywords) return
    setAutomation({
      ...automation,
      jobAlerts: [...automation.jobAlerts, {
        id: Date.now().toString(),
        ...newAlert,
        enabled: true
      }]
    })
    setNewAlert({ name: '', keywords: '', frequency: 'daily' })
  }

  const toggleAlert = (id: string) => {
    setAutomation({
      ...automation,
      jobAlerts: automation.jobAlerts.map(a => a.id === id ? { ...a, enabled: !a.enabled } : a)
    })
  }

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-3xl mx-auto">
        <Link href="/dashboard/settings" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
            <Bot className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold dark:text-white">Automation</h1>
            <p className="text-gray-600 dark:text-gray-400">Set up auto-apply and job alerts</p>
          </div>
        </div>

        {saved && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
            ✓ Automation settings saved!
          </div>
        )}

        {/* Auto-Apply Settings */}
        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="dark:text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  Auto-Apply (Beta)
                </CardTitle>
                <CardDescription className="dark:text-gray-400">Automatically apply to matching jobs</CardDescription>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={automation.autoApplyEnabled}
                  onChange={(e) => setAutomation({ ...automation, autoApplyEnabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </CardHeader>
          {automation.autoApplyEnabled && (
            <CardContent className="space-y-4">
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  ⚠️ Auto-apply will use your default resume and cover letter templates. Make sure they're up to date!
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Max Applications Per Day
                  </label>
                  <select
                    value={automation.maxAppsPerDay}
                    onChange={(e) => setAutomation({ ...automation, maxAppsPerDay: parseInt(e.target.value) })}
                    className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  >
                    <option value={5}>5 per day</option>
                    <option value={10}>10 per day</option>
                    <option value={20}>20 per day</option>
                    <option value={50}>50 per day</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Schedule
                  </label>
                  <select
                    value={automation.autoApplySchedule}
                    onChange={(e) => setAutomation({ ...automation, autoApplySchedule: e.target.value })}
                    className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  >
                    <option value="weekdays">Weekdays only</option>
                    <option value="daily">Every day</option>
                    <option value="business_hours">Business hours (9-17)</option>
                  </select>
                </div>
              </div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={automation.requiresReview}
                  onChange={(e) => setAutomation({ ...automation, requiresReview: e.target.checked })}
                  className="w-5 h-5 rounded"
                />
                <div>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">Require review before applying</span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Get notified to approve applications</p>
                </div>
              </label>
            </CardContent>
          )}
        </Card>

        {/* Job Alerts */}
        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="dark:text-white flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Job Alerts
            </CardTitle>
            <CardDescription className="dark:text-gray-400">Get notified when matching jobs are posted</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {automation.jobAlerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">{alert.name}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{alert.keywords}</div>
                  <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {alert.frequency === 'daily' ? '📅 Daily' : '📅 Weekly'}
                  </div>
                </div>
                <button
                  onClick={() => toggleAlert(alert.id)}
                  className={`p-2 rounded-lg ${alert.enabled ? 'bg-green-100 dark:bg-green-900 text-green-600' : 'bg-gray-200 dark:bg-gray-600 text-gray-500'}`}
                >
                  {alert.enabled ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
                </button>
              </div>
            ))}

            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Add New Alert</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <SketchInput
                  type="text"
                  placeholder="Alert name"
                  value={newAlert.name}
                  onChange={(e) => setNewAlert({ ...newAlert, name: e.target.value })}
                  className="w-full"
                />
                <SketchInput
                  type="text"
                  placeholder="Keywords (comma-separated)"
                  value={newAlert.keywords}
                  onChange={(e) => setNewAlert({ ...newAlert, keywords: e.target.value })}
                  className="w-full"
                />
                <SketchButton onClick={addAlert} variant="secondary">Add Alert</SketchButton>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <SketchButton onClick={handleSave} variant="primary" disabled={saving} className="flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Automation'}
          </SketchButton>
        </div>
      </div>
    </div>
  )
}
