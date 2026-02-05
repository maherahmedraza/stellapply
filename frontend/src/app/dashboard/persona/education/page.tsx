'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, GraduationCap, Plus, Trash2, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"
import { getPersona, addEducation, deleteEducation, type Education } from '@/lib/api/persona'

const degreeLabels: Record<string, string> = {
    'HIGH_SCHOOL': 'High School',
    'ASSOCIATE': 'Associate Degree',
    'BACHELOR': "Bachelor's Degree",
    'MASTER': "Master's Degree",
    'DOCTORATE': 'Doctorate',
    'CERTIFICATE': 'Certificate',
    'OTHER': 'Other',
}

export default function EducationPage() {
    const [educations, setEducations] = useState<Education[]>([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [showForm, setShowForm] = useState(false)
    const [newEdu, setNewEdu] = useState({
        institution_name: '',
        degree_type: 'BACHELOR' as Education['degree_type'],
        field_of_study: '',
        graduation_date: '',
        gpa: undefined as number | undefined,
    })

    useEffect(() => {
        loadEducation()
    }, [])

    const loadEducation = async () => {
        setLoading(true)
        try {
            const persona = await getPersona()
            if (persona?.educations) {
                setEducations(persona.educations)
            }
        } catch (err) {
            setError('Failed to load education')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleAddEducation = async () => {
        if (!newEdu.institution_name || !newEdu.field_of_study || !newEdu.graduation_date) {
            setError('Please fill in required fields')
            return
        }
        setSaving(true)
        setError(null)
        try {
            const edu = await addEducation(newEdu)
            setEducations([...educations, edu])
            setNewEdu({ institution_name: '', degree_type: 'BACHELOR', field_of_study: '', graduation_date: '', gpa: undefined })
            setShowForm(false)
        } catch (err) {
            setError('Failed to add education')
            console.error(err)
        } finally {
            setSaving(false)
        }
    }

    const handleDeleteEducation = async (id: string) => {
        try {
            await deleteEducation(id)
            setEducations(educations.filter(e => e.id !== id))
        } catch (err) {
            setError('Failed to delete education')
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
                        <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                            <GraduationCap className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold dark:text-white">Education</h1>
                            <p className="text-gray-600 dark:text-gray-400">Your academic background ({educations.length} entries)</p>
                        </div>
                    </div>
                    <SketchButton onClick={() => setShowForm(!showForm)} variant="secondary" className="flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Add Education
                    </SketchButton>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
                        ⚠️ {error}
                    </div>
                )}

                {/* Add Form */}
                {showForm && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6 border-purple-300 dark:border-purple-600">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Add Education</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Institution *</label>
                                <SketchInput
                                    type="text"
                                    placeholder="e.g., Technical University Berlin"
                                    value={newEdu.institution_name}
                                    onChange={(e) => setNewEdu({ ...newEdu, institution_name: e.target.value })}
                                    className="w-full"
                                />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Degree Type *</label>
                                    <select
                                        value={newEdu.degree_type}
                                        onChange={(e) => setNewEdu({ ...newEdu, degree_type: e.target.value as Education['degree_type'] })}
                                        className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                                    >
                                        {Object.entries(degreeLabels).map(([value, label]) => (
                                            <option key={value} value={value}>{label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Field of Study *</label>
                                    <SketchInput
                                        type="text"
                                        placeholder="e.g., Computer Science"
                                        value={newEdu.field_of_study}
                                        onChange={(e) => setNewEdu({ ...newEdu, field_of_study: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Graduation Date *</label>
                                    <SketchInput
                                        type="date"
                                        value={newEdu.graduation_date}
                                        onChange={(e) => setNewEdu({ ...newEdu, graduation_date: e.target.value })}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">GPA (optional)</label>
                                    <SketchInput
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        max="4"
                                        placeholder="e.g., 3.8"
                                        value={newEdu.gpa ?? ''}
                                        onChange={(e) => setNewEdu({ ...newEdu, gpa: e.target.value ? parseFloat(e.target.value) : undefined })}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end gap-2">
                                <SketchButton onClick={() => setShowForm(false)} variant="secondary">Cancel</SketchButton>
                                <SketchButton onClick={handleAddEducation} variant="primary" disabled={saving} className="flex items-center gap-2">
                                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                                    {saving ? 'Saving...' : 'Add Education'}
                                </SketchButton>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Education List */}
                {educations.map((edu) => (
                    <Card key={edu.id} className="dark:bg-gray-800 dark:border-gray-700 mb-4">
                        <CardContent className="pt-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-lg font-bold dark:text-white">{degreeLabels[edu.degree_type]} in {edu.field_of_study}</h3>
                                    <p className="text-purple-600 dark:text-purple-400 font-medium">{edu.institution_name}</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        Graduated: {new Date(edu.graduation_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                                        {edu.gpa && <span className="ml-2">• GPA: {edu.gpa.toFixed(2)}</span>}
                                    </p>
                                </div>
                                <button onClick={() => edu.id && handleDeleteEducation(edu.id)} className="text-red-500 hover:text-red-700 p-2">
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {educations.length === 0 && !showForm && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardContent className="py-12 text-center">
                            <GraduationCap className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400">No education added yet.</p>
                            <SketchButton onClick={() => setShowForm(true)} variant="primary" className="mt-4">
                                Add Your First Degree
                            </SketchButton>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
