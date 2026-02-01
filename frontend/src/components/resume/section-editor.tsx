'use client'

import { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
    GripVertical,
    ChevronDown,
    Sparkles,
    Plus,
    Trash2,
    Eye,
    EyeOff,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ResumeSection } from '@/stores/resume.store'

interface SectionEditorProps {
    section: ResumeSection
    onUpdate: (data: Partial<ResumeSection>) => void
    onEnhance: () => void
    isEnhancing: boolean
}

interface Experience {
    id: string
    company: string
    title: string
    startDate: string
    endDate: string
    description: string
    achievements: string[]
}

interface Education {
    id: string
    school: string
    degree: string
    year: string
}

export function SectionEditor({
    section,
    onUpdate,
    onEnhance,
    isEnhancing,
}: SectionEditorProps) {
    const [isOpen, setIsOpen] = useState(true)

    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: section.id })

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    }

    const renderSectionContent = () => {
        switch (section.type) {
            case 'summary':
                return (
                    <SummaryEditor
                        content={section.content as string}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
            case 'experience':
                return (
                    <ExperienceEditor
                        experiences={section.content as Experience[]}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
            case 'education':
                return (
                    <EducationEditor
                        education={section.content as Education[]}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
            case 'skills':
                return (
                    <SkillsEditor
                        skills={section.content as string[]}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
            default:
                return (
                    <CustomEditor
                        content={section.content}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
        }
    }

    return (
        <Card
            ref={setNodeRef}
            style={style}
            className={cn(
                'transition-shadow',
                isDragging && 'shadow-lg ring-2 ring-primary',
                !section.isVisible && 'opacity-60'
            )}
        >
            <Collapsible open={isOpen} onOpenChange={setIsOpen}>
                <CardHeader className="p-4">
                    <div className="flex items-center gap-2">
                        <button
                            {...attributes}
                            {...listeners}
                            className="cursor-grab active:cursor-grabbing p-1 hover:bg-gray-100 rounded"
                        >
                            <GripVertical className="h-5 w-5 text-gray-400" />
                        </button>

                        <CollapsibleTrigger asChild>
                            <Button variant="ghost" className="flex-1 justify-start gap-2">
                                <ChevronDown
                                    className={cn(
                                        'h-4 w-4 transition-transform',
                                        isOpen && 'rotate-180'
                                    )}
                                />
                                <span className="font-medium">{section.title}</span>
                            </Button>
                        </CollapsibleTrigger>

                        <div className="flex items-center gap-2">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={onEnhance}
                                disabled={isEnhancing}
                                className="gap-1"
                            >
                                <Sparkles className={cn(
                                    'h-4 w-4',
                                    isEnhancing && 'animate-pulse'
                                )} />
                                {isEnhancing ? 'Enhancing...' : 'AI Enhance'}
                            </Button>

                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => onUpdate({ isVisible: !section.isVisible })}
                            >
                                {section.isVisible ? (
                                    <Eye className="h-4 w-4" />
                                ) : (
                                    <EyeOff className="h-4 w-4" />
                                )}
                            </Button>
                        </div>
                    </div>
                </CardHeader>

                <CollapsibleContent>
                    <CardContent className="pt-0 pb-4">
                        {renderSectionContent()}
                    </CardContent>
                </CollapsibleContent>
            </Collapsible>
        </Card>
    )
}

function SummaryEditor({ content, onChange }: { content: string, onChange: (val: string) => void }) {
    return (
        <Textarea
            value={content}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Write your professional summary..."
            className="min-h-[150px]"
        />
    )
}

function ExperienceEditor({
    experiences,
    onChange,
}: {
    experiences: Experience[]
    onChange: (experiences: Experience[]) => void
}) {
    const addExperience = () => {
        onChange([
            ...(experiences || []),
            {
                id: crypto.randomUUID(),
                company: '',
                title: '',
                startDate: '',
                endDate: '',
                description: '',
                achievements: [''],
            },
        ])
    }

    const updateExperience = (index: number, updates: Partial<Experience>) => {
        const updated = [...experiences]
        updated[index] = { ...updated[index], ...updates }
        onChange(updated)
    }

    const removeExperience = (index: number) => {
        onChange(experiences.filter((_, i) => i !== index))
    }

    const addAchievement = (expIndex: number) => {
        const updated = [...experiences]
        updated[expIndex].achievements.push('')
        onChange(updated)
    }

    const updateAchievement = (expIndex: number, achIndex: number, value: string) => {
        const updated = [...experiences]
        updated[expIndex].achievements[achIndex] = value
        onChange(updated)
    }

    return (
        <div className="space-y-6">
            {(experiences || []).map((exp, expIndex) => (
                <div key={exp.id} className="border rounded-lg p-4 space-y-4">
                    <div className="flex justify-between items-start">
                        <div className="grid grid-cols-2 gap-4 flex-1">
                            <div className="space-y-2">
                                <Label>Company</Label>
                                <Input
                                    value={exp.company}
                                    onChange={(e) => updateExperience(expIndex, { company: e.target.value })}
                                    placeholder="Company Name"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Job Title</Label>
                                <Input
                                    value={exp.title}
                                    onChange={(e) => updateExperience(expIndex, { title: e.target.value })}
                                    placeholder="Job Title"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Start Date</Label>
                                <Input
                                    type="month"
                                    value={exp.startDate}
                                    onChange={(e) => updateExperience(expIndex, { startDate: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>End Date</Label>
                                <Input
                                    type="month"
                                    value={exp.endDate}
                                    onChange={(e) => updateExperience(expIndex, { endDate: e.target.value })}
                                    placeholder="Present"
                                />
                            </div>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeExperience(expIndex)}
                            className="text-red-500"
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>

                    <div className="space-y-2">
                        <Label>Achievements</Label>
                        {exp.achievements.map((achievement, achIndex) => (
                            <div key={achIndex} className="flex gap-2">
                                <Textarea
                                    value={achievement}
                                    onChange={(e) => updateAchievement(expIndex, achIndex, e.target.value)}
                                    placeholder="• Describe an achievement with quantifiable results..."
                                    className="min-h-[60px]"
                                />
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => {
                                        const updated = [...experiences]
                                        updated[expIndex].achievements = updated[expIndex].achievements.filter(
                                            (_, i) => i !== achIndex
                                        )
                                        onChange(updated)
                                    }}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        ))}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => addAchievement(expIndex)}
                            className="gap-1"
                        >
                            <Plus className="h-4 w-4" />
                            Add Achievement
                        </Button>
                    </div>
                </div>
            ))}

            <Button
                variant="dashed"
                onClick={addExperience}
                className="w-full gap-2"
            >
                <Plus className="h-4 w-4" />
                Add Experience
            </Button>
        </div>
    )
}

function EducationEditor({ education, onChange }: { education: Education[], onChange: (val: Education[]) => void }) {
    // Placeholder for education logic
    return (
        <div className="text-center text-muted-foreground p-4">
            Education editor needs implementation.
            <Button variant="dashed" className="w-full mt-4" onClick={() => onChange([...education, { id: crypto.randomUUID(), school: 'New School', degree: '', year: '' }])}>
                Add Education
            </Button>
            {education?.map((edu, idx) => (
                <div key={edu.id} className="mt-2 border p-2">
                    <Input value={edu.school} onChange={(e) => {
                        const updated = [...education];
                        updated[idx].school = e.target.value;
                        onChange(updated);
                    }} />
                </div>
            ))}
        </div>
    )
}

function SkillsEditor({ skills, onChange }: { skills: string[], onChange: (val: string[]) => void }) {
    return (
        <div className="text-center text-muted-foreground p-4">
            <Textarea value={skills?.join(', ')} onChange={(e) => onChange(e.target.value.split(',').map(s => s.trim()))} placeholder="Comma separated skills..." />
        </div>
    )
}


function CustomEditor({ content, onChange }: { content: unknown, onChange: (val: unknown) => void }) {
    void content;
    void onChange;
    return (
        <div className="text-center text-muted-foreground p-4">
            Custom section content.
        </div>
    )
}
