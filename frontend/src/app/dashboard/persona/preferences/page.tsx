'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Target, Save, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"
import { getPersona, updateCareerPreference, type CareerPreference } from '@/lib/api/persona'

export default function PreferencesPage() {
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [saved, setSaved] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [formData, setFormData] = useState<CareerPreference>({
        target_titles: [],
        target_industries: [],
        salary_min: undefined,
        salary_max: undefined,
        company_sizes: [],
        blacklisted_companies: [],
        dream_companies: [],
    })
    const [newTitle, setNewTitle] = useState('')
    const [newIndustry, setNewIndustry] = useState('')
    const [newDreamCompany, setNewDreamCompany] = useState('')

    useEffect(() => {
        loadPreferences()
    }, [])

    const loadPreferences = async () => {
        setLoading(true)
        try {
            const persona = await getPersona()
            if (persona?.career_preference) {
                setFormData(persona.career_preference)
            }
        } catch (err) {
            setError('Failed to load preferences')
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
            await updateCareerPreference(formData)
            setSaved(true)
            setTimeout(() => setSaved(false), 3000)
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to save preferences')
        } finally {
            setSaving(false)
        }
    }

    const addTitle = () => {
        if (newTitle.trim() && !formData.target_titles.includes(newTitle.trim())) {
            setFormData({ ...formData, target_titles: [...formData.target_titles, newTitle.trim()] })
            setNewTitle('')
        }
    }

    const addIndustry = () => {
        if (newIndustry.trim() && !formData.target_industries.includes(newIndustry.trim())) {
            setFormData({ ...formData, target_industries: [...formData.target_industries, newIndustry.trim()] })
            setNewIndustry('')
        }
    }

    const addDreamCompany = () => {
        if (newDreamCompany.trim() && !formData.dream_companies.includes(newDreamCompany.trim())) {
            setFormData({ ...formData, dream_companies: [...formData.dream_companies, newDreamCompany.trim()] })
            setNewDreamCompany('')
        }
    }

    const toggleCompanySize = (size: CareerPreference['company_sizes'][number]) => {
        if (formData.company_sizes.includes(size)) {
            setFormData({ ...formData, company_sizes: formData.company_sizes.filter(s => s !== size) })
        } else {
            setFormData({ ...formData, company_sizes: [...formData.company_sizes, size] })
        }
    }

    if (loading) {
        return (
            <div className="p-6 dark:bg-gray-900 min-h-screen flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        )
    }

    const companySizeOptions: { value: CareerPreference['company_sizes'][number]; label: string }[] = [
        { value: 'STARTUP', label: 'Startup (1-50)' },
        { value: 'SMALL', label: 'Small (51-200)' },
        { value: 'MEDIUM', label: 'Medium (201-1000)' },
        { value: 'LARGE', label: 'Large (1001-5000)' },
        { value: 'ENTERPRISE', label: 'Enterprise (5000+)' },
    ]

    return (
        <div className="p-6 dark:bg-gray-900 min-h-screen">
            <div className="max-w-3xl mx-auto">
                <Link href="/dashboard/persona" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Persona
                </Link>

                <div className="flex items-center gap-4 mb-8">
                    <div className="w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
                        <Target className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold dark:text-white">Career Goals</h1>
                        <p className="text-gray-600 dark:text-gray-400">Your job search preferences and targets</p>
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

                <form onSubmit={handleSubmit}>
                    {/* Target Titles */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Target Job Titles</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <SketchInput
                                    type="text"
                                    placeholder="e.g., Senior Data Engineer"
                                    value={newTitle}
                                    onChange={(e) => setNewTitle(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTitle())}
                                    className="flex-1"
                                />
                                <SketchButton type="button" onClick={addTitle} variant="secondary">Add</SketchButton>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {formData.target_titles.map((title, i) => (
                                    <span key={i} className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full flex items-center gap-2">
                                        {title}
                                        <button type="button" onClick={() => setFormData({ ...formData, target_titles: formData.target_titles.filter((_, idx) => idx !== i) })} className="text-blue-500 hover:text-blue-700 text-lg leading-none">&times;</button>
                                    </span>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Target Industries */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Target Industries</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <SketchInput
                                    type="text"
                                    placeholder="e.g., FinTech, Healthcare"
                                    value={newIndustry}
                                    onChange={(e) => setNewIndustry(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addIndustry())}
                                    className="flex-1"
                                />
                                <SketchButton type="button" onClick={addIndustry} variant="secondary">Add</SketchButton>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {formData.target_industries.map((industry, i) => (
                                    <span key={i} className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full flex items-center gap-2">
                                        {industry}
                                        <button type="button" onClick={() => setFormData({ ...formData, target_industries: formData.target_industries.filter((_, idx) => idx !== i) })} className="text-green-500 hover:text-green-700 text-lg leading-none">&times;</button>
                                    </span>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Salary Range */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Salary Expectations (EUR/year)</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Minimum</label>
                                    <SketchInput
                                        type="number"
                                        placeholder="70000"
                                        value={formData.salary_min ?? ''}
                                        onChange={(e) => setFormData({ ...formData, salary_min: e.target.value ? parseInt(e.target.value) : undefined })}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Maximum</label>
                                    <SketchInput
                                        type="number"
                                        placeholder="100000"
                                        value={formData.salary_max ?? ''}
                                        onChange={(e) => setFormData({ ...formData, salary_max: e.target.value ? parseInt(e.target.value) : undefined })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Company Size */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Preferred Company Sizes</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-3">
                                {companySizeOptions.map((option) => (
                                    <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={formData.company_sizes.includes(option.value)}
                                            onChange={() => toggleCompanySize(option.value)}
                                            className="w-4 h-4"
                                        />
                                        <span className="text-gray-700 dark:text-gray-300">{option.label}</span>
                                    </label>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Dream Companies */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Dream Companies</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <SketchInput
                                    type="text"
                                    placeholder="e.g., Google, Spotify"
                                    value={newDreamCompany}
                                    onChange={(e) => setNewDreamCompany(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addDreamCompany())}
                                    className="flex-1"
                                />
                                <SketchButton type="button" onClick={addDreamCompany} variant="secondary">Add</SketchButton>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {formData.dream_companies.map((company, i) => (
                                    <span key={i} className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full flex items-center gap-2">
                                        ⭐ {company}
                                        <button type="button" onClick={() => setFormData({ ...formData, dream_companies: formData.dream_companies.filter((_, idx) => idx !== i) })} className="text-purple-500 hover:text-purple-700 text-lg leading-none">&times;</button>
                                    </span>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    <div className="flex justify-end">
                        <SketchButton type="submit" variant="primary" disabled={saving} className="flex items-center gap-2">
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            {saving ? 'Saving...' : 'Save Preferences'}
                        </SketchButton>
                    </div>
                </form>
            </div>
        </div>
    )
}
