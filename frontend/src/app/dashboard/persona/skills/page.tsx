'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, Plus, Trash2, Save, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"
import { getPersona, addSkill, deleteSkill, type Skill } from '@/lib/api/persona'

const levelColors: Record<number, string> = {
    1: 'bg-gray-200 dark:bg-gray-600',
    2: 'bg-blue-200 dark:bg-blue-700',
    3: 'bg-green-200 dark:bg-green-700',
    4: 'bg-purple-200 dark:bg-purple-700',
    5: 'bg-yellow-200 dark:bg-yellow-700',
}

const levelLabels: Record<number, string> = {
    1: 'Beginner',
    2: 'Elementary',
    3: 'Intermediate',
    4: 'Advanced',
    5: 'Expert',
}

export default function SkillsPage() {
    const [skills, setSkills] = useState<Skill[]>([])
    const [newSkill, setNewSkill] = useState('')
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        loadSkills()
    }, [])

    const loadSkills = async () => {
        setLoading(true)
        try {
            const persona = await getPersona()
            if (persona?.skills) {
                setSkills(persona.skills)
            }
        } catch (err) {
            setError('Failed to load skills')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleAddSkill = async () => {
        if (!newSkill.trim()) return
        setSaving(true)
        try {
            const skill = await addSkill({
                name: newSkill,
                category: 'TECHNICAL',
                proficiency_level: 3,
            })
            setSkills([...skills, skill])
            setNewSkill('')
        } catch (err) {
            setError('Failed to add skill')
            console.error(err)
        } finally {
            setSaving(false)
        }
    }

    const handleDeleteSkill = async (id: string) => {
        try {
            await deleteSkill(id)
            setSkills(skills.filter(s => s.id !== id))
        } catch (err) {
            setError('Failed to delete skill')
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

    const technicalSkills = skills.filter(s => s.category === 'TECHNICAL')
    const toolSkills = skills.filter(s => s.category === 'TOOL')
    const otherSkills = skills.filter(s => !['TECHNICAL', 'TOOL'].includes(s.category))

    return (
        <div className="p-6 dark:bg-gray-900 min-h-screen">
            <div className="max-w-3xl mx-auto">
                <Link href="/dashboard/persona" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Persona
                </Link>

                <div className="flex items-center gap-4 mb-8">
                    <div className="w-16 h-16 rounded-full bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center">
                        <Star className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold dark:text-white">Skills</h1>
                        <p className="text-gray-600 dark:text-gray-400">Technical skills for your profile ({skills.length} total)</p>
                    </div>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
                        ⚠️ {error}
                    </div>
                )}

                {/* Add Skill */}
                <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                    <CardContent className="pt-6">
                        <div className="flex gap-2">
                            <SketchInput
                                type="text"
                                placeholder="Add a new skill (e.g., Python, Spark, AWS...)"
                                value={newSkill}
                                onChange={(e) => setNewSkill(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                                className="flex-1"
                            />
                            <SketchButton onClick={handleAddSkill} variant="secondary" disabled={saving} className="flex items-center gap-2">
                                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                                Add
                            </SketchButton>
                        </div>
                    </CardContent>
                </Card>

                {/* Technical Skills */}
                {technicalSkills.length > 0 && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Technical Skills ({technicalSkills.length})</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2">
                                {technicalSkills.map(skill => (
                                    <div key={skill.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg ${levelColors[skill.proficiency_level] || levelColors[3]}`}>
                                        <span className="font-medium text-gray-800 dark:text-white">{skill.name}</span>
                                        <span className="text-xs text-gray-600 dark:text-gray-300">
                                            {levelLabels[skill.proficiency_level]}
                                        </span>
                                        <button onClick={() => skill.id && handleDeleteSkill(skill.id)} className="text-red-500 hover:text-red-700 ml-1">
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Tools & Other Skills */}
                {(toolSkills.length > 0 || otherSkills.length > 0) && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardHeader>
                            <CardTitle className="dark:text-white">Tools & Other ({toolSkills.length + otherSkills.length})</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2">
                                {[...toolSkills, ...otherSkills].map(skill => (
                                    <div key={skill.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg ${levelColors[skill.proficiency_level] || levelColors[3]}`}>
                                        <span className="font-medium text-gray-800 dark:text-white">{skill.name}</span>
                                        <button onClick={() => skill.id && handleDeleteSkill(skill.id)} className="text-red-500 hover:text-red-700 ml-1">
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {skills.length === 0 && (
                    <Card className="dark:bg-gray-800 dark:border-gray-700 mb-6">
                        <CardContent className="py-8 text-center">
                            <Star className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400">No skills added yet. Add your first skill above!</p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
