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
    Eye,
    EyeOff,
    Trash2,
    Plus
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ResumeSection, ExperienceContent, EducationContent } from '@/stores/resume.store'

interface SectionEditorProps {
    section: ResumeSection
    onUpdate: (data: Partial<ResumeSection>) => void
    onEnhance: () => void
    isEnhancing: boolean
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
                        experiences={section.content as ExperienceContent[]}
                        onChange={(content) => onUpdate({ content })}
                    />
                )
            case 'education':
                return (
                    <EducationEditor
                        education={section.content as EducationContent[]}
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
                'transition-all border-2 border-border wobbly-md shadow-hand-sm bg-background-alt overflow-hidden mb-6',
                isDragging && 'shadow-hand-xl ring-4 ring-accent/20 border-accent z-50',
                !section.isVisible && 'opacity-60 grayscale-[0.5]'
            )}
        >
            <Collapsible open={isOpen} onOpenChange={setIsOpen}>
                <CardHeader className="p-4 bg-background-muted/30 border-b-2 border-dashed border-border mb-4">
                    <div className="flex items-center gap-3">
                        <button
                            {...attributes}
                            {...listeners}
                            className="cursor-grab active:cursor-grabbing p-1.5 hover:bg-background-alt wobbly-sm transition-colors"
                        >
                            <GripVertical className="h-5 w-5 text-foreground-subtle" />
                        </button>

                        <CollapsibleTrigger asChild>
                            <Button variant="ghost" className="flex-1 justify-start gap-2 hover:bg-background-alt wobbly-sm font-heading text-lg text-foreground">
                                <ChevronDown
                                    className={cn(
                                        'h-5 w-5 transition-transform text-accent',
                                        isOpen && 'rotate-180'
                                    )}
                                />
                                {section.title}
                            </Button>
                        </CollapsibleTrigger>

                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={onEnhance}
                                disabled={isEnhancing}
                                className="gap-2 wobbly-sm shadow-hand-sm border-2 border-border hover:bg-background-alt bg-background-alt"
                            >
                                <Sparkles className={cn(
                                    'h-4 w-4 text-accent',
                                    isEnhancing && 'animate-spin'
                                )} />
                                <span className="hidden sm:inline">{isEnhancing ? 'Enhancing...' : 'AI Enhance'}</span>
                            </Button>

                            <Button
                                variant="outline"
                                size="icon"
                                onClick={() => onUpdate({ isVisible: !section.isVisible })}
                                className="wobbly-sm border-2 border-border hover:bg-background-alt bg-background-alt"
                            >
                                {section.isVisible ? (
                                    <Eye className="h-4 w-4 text-foreground" />
                                ) : (
                                    <EyeOff className="h-4 w-4 text-foreground-subtle" />
                                )}
                            </Button>
                        </div>
                    </div>
                </CardHeader>

                <CollapsibleContent>
                    <CardContent className="p-6 pt-0">
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
            className="min-h-[160px] wobbly-sm border-2 border-border bg-background focus:ring-accent font-body text-base leading-relaxed"
        />
    )
}

function ExperienceEditor({
    experiences,
    onChange,
}: {
    experiences: ExperienceContent[]
    onChange: (experiences: ExperienceContent[]) => void
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

    const updateExperience = (index: number, updates: Partial<ExperienceContent>) => {
        const updated = [...experiences]
        updated[index] = { ...updated[index], ...updates }
        onChange(updated)
    }

    const removeExperience = (index: number) => {
        onChange(experiences.filter((_, i) => i !== index))
    }

    const addAchievement = (expIndex: number) => {
        const updated = JSON.parse(JSON.stringify(experiences))
        if (!updated[expIndex].achievements) {
            updated[expIndex].achievements = []
        }
        updated[expIndex].achievements.push('')
        onChange(updated)
    }

    const updateAchievement = (expIndex: number, achIndex: number, value: string) => {
        const updated = JSON.parse(JSON.stringify(experiences))
        updated[expIndex].achievements[achIndex] = value
        onChange(updated)
    }

    const removeAchievement = (expIndex: number, achIndex: number) => {
        const updated = JSON.parse(JSON.stringify(experiences))
        updated[expIndex].achievements = updated[expIndex].achievements.filter(
            (_: any, i: number) => i !== achIndex
        )
        onChange(updated)
    }

    return (
        <div className="space-y-8">
            {(experiences || []).map((exp, expIndex) => (
                <div key={exp.id || expIndex} className="wobbly-md border-2 border-border p-6 space-y-6 bg-background-alt shadow-hand-soft">
                    <div className="flex justify-between items-start gap-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 flex-1">
                            <div className="space-y-2">
                                <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle">Company</Label>
                                <Input
                                    value={exp.company}
                                    onChange={(e) => updateExperience(expIndex, { company: e.target.value })}
                                    placeholder="Company Name"
                                    className="wobbly-sm border-2 border-border focus:ring-accent font-body"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle">Job Title</Label>
                                <Input
                                    value={exp.title}
                                    onChange={(e) => updateExperience(expIndex, { title: e.target.value })}
                                    placeholder="Job Title"
                                    className="wobbly-sm border-2 border-border focus:ring-accent font-body"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle">Start Date</Label>
                                <Input
                                    type="month"
                                    value={exp.startDate}
                                    onChange={(e) => updateExperience(expIndex, { startDate: e.target.value })}
                                    className="wobbly-sm border-2 border-border focus:ring-accent font-body"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle">End Date</Label>
                                <Input
                                    type="month"
                                    value={exp.endDate}
                                    onChange={(e) => updateExperience(expIndex, { endDate: e.target.value })}
                                    className="wobbly-sm border-2 border-border focus:ring-accent font-body"
                                />
                            </div>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeExperience(expIndex)}
                            className="text-error hover:bg-error/10 wobbly-sm"
                        >
                            <Trash2 className="h-5 w-5" />
                        </Button>
                    </div>

                    <div className="space-y-4">
                        <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle block mb-1">Achievements & Impact</Label>
                        <div className="space-y-3">
                            {exp.achievements.map((achievement, achIndex) => (
                                <div key={achIndex} className="flex gap-2 group">
                                    <Textarea
                                        value={achievement}
                                        onChange={(e) => updateAchievement(expIndex, achIndex, e.target.value)}
                                        placeholder="• Describe an achievement with quantifiable results..."
                                        className="min-h-[80px] wobbly-sm border-2 border-border bg-background focus:ring-accent font-body resize-none"
                                    />
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => removeAchievement(expIndex, achIndex)}
                                        className="text-foreground-subtle hover:text-error hover:bg-error/10 wobbly-sm shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => addAchievement(expIndex)}
                            className="gap-2 wobbly-sm border-2 border-dashed border-border hover:border-accent hover:text-accent font-heading text-xs"
                        >
                            <Plus className="h-4 w-4" />
                            Add Achievement
                        </Button>
                    </div>
                </div>
            ))}

            <Button
                variant="outline"
                onClick={addExperience}
                className="w-full gap-3 py-8 wobbly-md border-2 border-dashed border-border hover:border-accent hover:bg-accent/5 hover:text-accent font-heading text-lg shadow-hand-sm"
            >
                <Plus className="h-6 w-6" />
                Add Work Experience
            </Button>
        </div>
    )
}

function EducationEditor({ education, onChange }: { education: EducationContent[], onChange: (val: EducationContent[]) => void }) {
    const addEducation = () => {
        onChange([
            ...(education || []),
            { id: crypto.randomUUID(), school: '', degree: '', year: '' }
        ])
    }

    const updateEducation = (index: number, updates: Partial<EducationContent>) => {
        const updated = [...education]
        updated[index] = { ...updated[index], ...updates }
        onChange(updated)
    }

    const removeEducation = (index: number) => {
        onChange(education.filter((_, i) => i !== index))
    }

    return (
        <div className="space-y-6">
            {(education || []).map((edu, idx) => (
                <div key={edu.id || idx} className="wobbly-sm border-2 border-border p-4 space-y-4 bg-background-alt shadow-hand-soft">
                    <div className="flex justify-between items-start gap-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
                            <Input
                                placeholder="School/University"
                                value={edu.school}
                                onChange={(e) => updateEducation(idx, { school: e.target.value })}
                                className="wobbly-sm border-2 border-border font-body"
                            />
                            <Input
                                placeholder="Degree/Certification"
                                value={edu.degree}
                                onChange={(e) => updateEducation(idx, { degree: e.target.value })}
                                className="wobbly-sm border-2 border-border font-body"
                            />
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeEducation(idx)}
                            className="text-error hover:bg-error/10 wobbly-sm"
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            ))}
            <Button
                variant="outline"
                className="w-full gap-2 wobbly-sm border-2 border-dashed border-border py-6 hover:text-accent hover:border-accent"
                onClick={addEducation}
            >
                <Plus className="h-4 w-4" />
                Add Education
            </Button>
        </div>
    )
}

function SkillsEditor({ skills, onChange }: { skills: string[], onChange: (val: string[]) => void }) {
    return (
        <div className="space-y-4">
            <Label className="font-heading text-sm uppercase tracking-wider text-foreground-subtle">List your skills (comma separated)</Label>
            <Textarea
                value={skills?.join(', ')}
                onChange={(e) => onChange(e.target.value.split(',').map(s => s.trim()))}
                placeholder="React, TypeScript, Python, AWS..."
                className="min-h-[120px] wobbly-sm border-2 border-border bg-background focus:ring-accent font-body text-base"
            />
            <p className="text-[11px] text-foreground-subtle font-body italic">
                Pro tip: Be specific and group related skills.
            </p>
        </div>
    )
}

function CustomEditor({ content, onChange }: { content: unknown, onChange: (val: unknown) => void }) {
    void content;
    void onChange;
    return (
        <div className="py-8 text-center wobbly-sm border-2 border-dashed border-border bg-background-muted">
            <p className="text-foreground-muted font-body">Custom section content logic coming soon.</p>
        </div>
    )
}
