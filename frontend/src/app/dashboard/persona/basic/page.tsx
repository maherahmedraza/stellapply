'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, User, Save, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"
import { getPersona, updatePersona, type Persona } from '@/lib/api/persona'

export default function BasicInfoPage() {
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [saved, setSaved] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [formData, setFormData] = useState<{
        full_name: string
        email: string
        phone: string
        location_city: string
        location_country: string
        work_authorization: Persona['work_authorization']
        remote_preference: Persona['remote_preference']
    }>({
        full_name: '',
        email: '',
        phone: '',
        location_city: '',
        location_country: '',
        work_authorization: 'NOT_REQUIRED',
        remote_preference: 'ANY',
    })

    useEffect(() => {
        loadPersona()
    }, [])

    const loadPersona = async () => {
        setLoading(true)
        setError(null)
        try {
            const persona = await getPersona()
            if (persona) {
                setFormData({
                    full_name: persona.full_name || '',
                    email: persona.email || '',
                    phone: persona.phone || '',
                    location_city: persona.location_city || '',
                    location_country: persona.location_country || '',
                    work_authorization: persona.work_authorization || 'NOT_REQUIRED',
                    remote_preference: persona.remote_preference || 'ANY',
                })
            }
        } catch (err) {
            setError('Failed to load profile. Please try again.')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)
        setError(null)
        try {
            await updatePersona(formData)
            setSaved(true)
            setTimeout(() => setSaved(false), 3000)
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to save profile')
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
                <Link href="/dashboard/persona" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Persona
                </Link>

                <div className="flex items-center gap-4 mb-8">
                    <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                        <User className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold dark:text-white">Basic Info</h1>
                        <p className="text-gray-600 dark:text-gray-400">Your personal and contact information</p>
                    </div>
                </div>

                {saved && (
                    <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
                        ✓ Profile saved successfully!
                    </div>
                )}

                {error && (
                    <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
                        ⚠️ {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Personal Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name *</label>
                                <SketchInput
                                    type="text"
                                    placeholder="John Doe"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    required
                                    className="w-full"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
                                <SketchInput
                                    type="email"
                                    placeholder="john.doe@example.com"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                    className="w-full"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
                                <SketchInput
                                    type="tel"
                                    placeholder="+49 123 456 7890"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    className="w-full"
                                />
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Location</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">City</label>
                                    <SketchInput
                                        type="text"
                                        placeholder="Berlin"
                                        value={formData.location_city}
                                        onChange={(e) => setFormData({ ...formData, location_city: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
                                    <SketchInput
                                        type="text"
                                        placeholder="Germany"
                                        value={formData.location_country}
                                        onChange={(e) => setFormData({ ...formData, location_country: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Work Preferences</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Work Authorization</label>
                                <select
                                    value={formData.work_authorization}
                                    onChange={(e) => setFormData({ ...formData, work_authorization: e.target.value as Persona['work_authorization'] })}
                                    className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                                >
                                    <option value="NOT_REQUIRED">No Visa Required (EU/Citizen)</option>
                                    <option value="CITIZEN">US Citizen</option>
                                    <option value="PERMANENT_RESIDENT">Permanent Resident / Green Card</option>
                                    <option value="H1B">H1B Visa</option>
                                    <option value="L1">L1 Visa</option>
                                    <option value="F1_OPT">F1 OPT</option>
                                    <option value="J1">J1 Visa</option>
                                    <option value="TN">TN Visa</option>
                                    <option value="OTHER">Other</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Remote Preference</label>
                                <div className="flex gap-4 flex-wrap">
                                    {[
                                        { value: 'REMOTE', label: 'Fully Remote' },
                                        { value: 'HYBRID', label: 'Hybrid' },
                                        { value: 'ONSITE', label: 'On-site' },
                                        { value: 'ANY', label: 'Any' },
                                    ].map((option) => (
                                        <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                                            <input
                                                type="radio"
                                                name="remote"
                                                value={option.value}
                                                checked={formData.remote_preference === option.value}
                                                onChange={(e) => setFormData({ ...formData, remote_preference: e.target.value as Persona['remote_preference'] })}
                                                className="w-4 h-4"
                                            />
                                            <span className="text-gray-700 dark:text-gray-300">{option.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <div className="flex justify-end">
                        <SketchButton type="submit" variant="primary" disabled={saving} className="flex items-center gap-2">
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            {saving ? 'Saving...' : 'Save Basic Info'}
                        </SketchButton>
                    </div>
                </form>
            </div>
        </div>
    )
}
