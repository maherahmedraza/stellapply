'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Briefcase, Plus, Trash2, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"
import { getPersona, addExperience, deleteExperience, type Experience } from '@/lib/api/persona'

export default function ExperiencePage() {
    const [experiences, setExperiences] = useState<Experience[]>([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [showForm, setShowForm] = useState(false)
    const [newExp, setNewExp] = useState({
        job_title: '',
        company_name: '',
        start_date: '',
        end_date: '',
        description: '',
        achievements: [] as string[],
        skills_used: [] as string[],
    })

    useEffect(() => {
        loadExperiences()
    }, [])

    const loadExperiences = async () => {
        setLoading(true)
        try {
            const persona = await getPersona()
            if (persona?.experiences) {
                setExperiences(persona.experiences)
            }
        } catch (err) {
            setError('Failed to load experiences')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleAddExperience = async () => {
        if (!newExp.job_title || !newExp.company_name || !newExp.start_date) {
            setError('Please fill in required fields')
            return
        }
        setSaving(true)
        setError(null)
        try {
            const exp = await addExperience(newExp)
            setExperiences([...experiences, exp])
            setNewExp({ job_title: '', company_name: '', start_date: '', end_date: '', description: '', achievements: [], skills_used: [] })
            setShowForm(false)
        } catch (err) {
            setError('Failed to add experience')
            console.error(err)
        } finally {
            setSaving(false)
        }
    }

    const handleDeleteExperience = async (id: string) => {
        try {
            await deleteExperience(id)
            setExperiences(experiences.filter(e => e.id !== id))
        } catch (err) {
            setError('Failed to delete experience')
            console.error(err)
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

                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                            <Briefcase className="w-8 h-8 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold dark:text-white">Experience</h1>
                            <p className="text-gray-600 dark:text-gray-400">Your work history ({experiences.length} positions)</p>
                        </div>
                    </div>
                    <SketchButton onClick={() => setShowForm(!showForm)} variant="secondary" className="flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Add Experience
                    </SketchButton>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
                        ⚠️ {error}
                    </div>
                )}

                {/* Add Form */}
                {showForm && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6 border-blue-300 dark:border-blue-600">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Add New Experience</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Job Title *</label>
                                    <SketchInput
                                        type="text"
                                        placeholder="e.g., Senior Data Engineer"
                                        value={newExp.job_title}
                                        onChange={(e) => setNewExp({ ...newExp, job_title: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company *</label>
                                    <SketchInput
                                        type="text"
                                        placeholder="e.g., Tech Company GmbH"
                                        value={newExp.company_name}
                                        onChange={(e) => setNewExp({ ...newExp, company_name: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date *</label>
                                    <SketchInput
                                        type="date"
                                        value={newExp.start_date}
                                        onChange={(e) => setNewExp({ ...newExp, start_date: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date (leave blank if current)</label>
                                    <SketchInput
                                        type="date"
                                        value={newExp.end_date}
                                        onChange={(e) => setNewExp({ ...newExp, end_date: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                                <textarea
                                    placeholder="Describe your responsibilities and achievements..."
                                    value={newExp.description}
                                    onChange={(e) => setNewExp({ ...newExp, description: e.target.value })}
                                    className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white min-h-[100px]"
                                />
                            </div>
                            <div className="flex justify-end gap-2">
                                <SketchButton onClick={() => setShowForm(false)} variant="secondary">Cancel</SketchButton>
                                <SketchButton onClick={handleAddExperience} variant="primary" disabled={saving} className="flex items-center gap-2">
                                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                                    {saving ? 'Saving...' : 'Add Experience'}
                                </SketchButton>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Experience List */}
                {experiences.map((exp) => (
                    <Card key={exp.id} className="dark:bg-gray-800 dark:border-gray-700 mb-4">
                        <CardContent className="pt-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-lg font-bold dark:text-white">{exp.job_title}</h3>
                                    <p className="text-blue-600 dark:text-blue-400 font-medium">{exp.company_name}</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        {new Date(exp.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                                        {' - '}
                                        {exp.end_date ? new Date(exp.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Present'}
                                    </p>
                                    {exp.description && (
                                        <p className="text-gray-600 dark:text-gray-300 mt-2">{exp.description}</p>
                                    )}
                                </div>
                                <button onClick={() => exp.id && handleDeleteExperience(exp.id)} className="text-red-500 hover:text-red-700 p-2">
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {experiences.length === 0 && !showForm && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardContent className="py-12 text-center">
                            <Briefcase className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400">No work experience added yet.</p>
                            <SketchButton onClick={() => setShowForm(true)} variant="primary" className="mt-4">
                                Add Your First Position
                            </SketchButton>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
