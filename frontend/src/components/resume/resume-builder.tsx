'use client'

import { useState, useCallback, useEffect } from 'react'
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ResumePreview, ATSScoreCard, TemplateSelector } from './placeholders'
import { useResumeStore, ExperienceContent } from '@/stores/resume.store'
import {
    FileText,
    Eye,
    BarChart2,
    Sparkles,
    Download,
    Save,
    AlertCircle,
    Check
} from 'lucide-react'
import { SectionEditor } from './section-editor'
import { AIEnhancementPanel } from './ai-enhancement-panel'
import { cn } from '@/lib/utils'

interface ResumeBuilderProps {
    resumeId?: string
}

export function ResumeBuilder({ resumeId }: ResumeBuilderProps) {
    const [activeTab, setActiveTab] = useState('edit')
    const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null)
    const [showAIPanel, setShowAIPanel] = useState(false)
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

    const {
        resume,
        sections,
        atsScore,
        isLoading,
        isSaving,
        error,
        updateSection,
        reorderSections,
        analyzeATS,
        downloadResume,
        updateResume,
        loadResume,
        saveResume,
        clearError
    } = useResumeStore()

    useEffect(() => {
        if (resumeId) {
            loadResume(resumeId)
        }
    }, [resumeId, loadResume])

    const handleDragEnd = useCallback((event: DragEndEvent) => {
        const { active, over } = event
        if (over && active.id !== over.id) {
            reorderSections(active.id as string, over.id as string)
        }
    }, [reorderSections])

    const handleSave = async () => {
        setSaveStatus('saving')
        try {
            await saveResume()
            setSaveStatus('saved')
            setTimeout(() => setSaveStatus('idle'), 3000)
        } catch (err) {
            setSaveStatus('error')
            setTimeout(() => setSaveStatus('idle'), 5000)
        }
    }

    const handleEnhanceClick = (sectionId: string) => {
        setSelectedSectionId(sectionId)
        setShowAIPanel(true)
    }

    const handleApplySuggestion = (text: string) => {
        if (!selectedSectionId) return

        const section = sections.find(s => s.id === selectedSectionId)
        if (!section) return

        if (section.type === 'summary') {
            updateSection(selectedSectionId, { content: text })
        } else if (section.type === 'experience') {
            const experiences = section.content as ExperienceContent[]
            if (experiences && experiences.length > 0) {
                const newExperiences = JSON.parse(JSON.stringify(experiences))
                // For now, applying to the first achievement of the first experience
                // In a real app, you'd pick the specific one
                if (newExperiences[0].achievements && newExperiences[0].achievements.length > 0) {
                    newExperiences[0].achievements[0] = text
                } else {
                    newExperiences[0].description = text
                }
                updateSection(selectedSectionId, { content: newExperiences })
            }
        }
    }

    if (isLoading) {
        return <LoadingState />
    }

    return (
        <div className="flex flex-col h-screen overflow-hidden bg-background">
            {/* Top Toolbar */}
            <header className="h-16 border-b-2 border-border bg-background-alt px-6 flex items-center justify-between z-10">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 wobbly-circle bg-accent flex items-center justify-center shadow-hand-sm">
                        <FileText className="text-white h-5 w-5" />
                    </div>
                    <div>
                        <h1 className="font-heading text-lg leading-tight">{resume?.title || 'New Resume'}</h1>
                        <p className="text-[10px] uppercase tracking-widest text-foreground-subtle font-heading">
                            {resume?.personaId ? 'Grounded in Persona' : 'Draft'}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSave}
                        disabled={isSaving}
                        className={cn(
                            "wobbly-sm border-2 border-border shadow-hand-sm gap-2 transition-all",
                            saveStatus === 'saved' && "border-success text-success bg-success/5"
                        )}
                    >
                        {saveStatus === 'saving' ? (
                            <div className="animate-spin h-4 w-4 border-2 border-accent border-t-transparent rounded-full" />
                        ) : saveStatus === 'saved' ? (
                            <Check className="h-4 w-4" />
                        ) : (
                            <Save className="h-4 w-4" />
                        )}
                        {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? 'Saved' : 'Save Draft'}
                    </Button>

                    <div className="w-px h-6 bg-border mx-1" />

                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadResume('pdf')}
                        className="wobbly-sm border-2 border-border shadow-hand-sm gap-2"
                    >
                        <Download className="h-4 w-4" />
                        Export
                    </Button>
                </div>
            </header>

            <main className="flex-1 flex overflow-hidden">
                {/* Left Panel - Editor */}
                <div className="w-1/2 flex flex-col border-r-2 border-border bg-background overflow-hidden">
                    {error && (
                        <div className="p-4 bg-error/10 border-b-2 border-error text-error text-sm flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <AlertCircle className="h-4 w-4" />
                                <span>{error}</span>
                            </div>
                            <Button variant="ghost" size="sm" onClick={clearError}>Dismiss</Button>
                        </div>
                    )}

                    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                        <div className="p-4 border-b-2 border-dashed border-border flex items-center justify-between bg-background-muted/20">
                            <TabsList className="bg-background-muted border-2 border-border wobbly-sm p-1">
                                <TabsTrigger value="edit" className="gap-2 font-heading text-xs uppercase data-[state=active]:bg-background-alt">
                                    <FileText className="h-3.5 w-3.5" />
                                    Edit Content
                                </TabsTrigger>
                                <TabsTrigger value="template" className="gap-2 font-heading text-xs uppercase data-[state=active]:bg-background-alt">
                                    <Eye className="h-3.5 w-3.5" />
                                    Templates
                                </TabsTrigger>
                                <TabsTrigger value="ats" className="gap-2 font-heading text-xs uppercase data-[state=active]:bg-background-alt">
                                    <BarChart2 className="h-3.5 w-3.5" />
                                    ATS Score
                                </TabsTrigger>
                            </TabsList>

                            <Button
                                size="sm"
                                variant="outline"
                                onClick={() => analyzeATS()}
                                className="wobbly-sm border-2 border-border shadow-hand-sm font-heading text-[10px] uppercase tracking-wider"
                            >
                                <Sparkles className="h-3 w-3 mr-1.5 text-accent" />
                                Audit Resume
                            </Button>
                        </div>

                        <div className="flex-1 overflow-auto custom-scrollbar">
                            <TabsContent value="edit" className="m-0 p-6 space-y-2 outline-none">
                                <DndContext
                                    collisionDetection={closestCenter}
                                    onDragEnd={handleDragEnd}
                                >
                                    <SortableContext
                                        items={sections.map(s => s.id)}
                                        strategy={verticalListSortingStrategy}
                                    >
                                        {sections.map((section) => (
                                            <SectionEditor
                                                key={section.id}
                                                section={section}
                                                onUpdate={(data) => updateSection(section.id, data)}
                                                onEnhance={() => handleEnhanceClick(section.id)}
                                                isEnhancing={false} // Managed by AI panel now
                                            />
                                        ))}
                                    </SortableContext>
                                </DndContext>
                            </TabsContent>

                            <TabsContent value="template" className="m-0 p-6 outline-none">
                                <TemplateSelector
                                    currentTemplate={resume?.templateId}
                                    onSelect={(templateId) => updateResume({ templateId })}
                                />
                            </TabsContent>

                            <TabsContent value="ats" className="m-0 p-6 outline-none">
                                <ATSScoreCard
                                    score={atsScore}
                                    onReanalyze={analyzeATS}
                                />
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>

                {/* Right Panel - Preview */}
                <div className="flex-1 bg-background-muted/30 flex flex-col p-8 overflow-auto">
                    <div className="max-w-[800px] mx-auto w-full shadow-hand-xl wobbly-sm bg-white min-h-[1000px] p-12 border-2 border-border border-dashed">
                        <ResumePreview
                            resume={resume}
                            sections={sections}
                            template={resume?.templateId}
                        />
                    </div>
                </div>
            </main>

            {/* AI Enhancement Slide-over Panel */}
            <AIEnhancementPanel
                open={showAIPanel}
                onClose={() => setShowAIPanel(false)}
                section={sections.find(s => s.id === selectedSectionId)}
                onApplySuggestion={handleApplySuggestion}
            />
        </div>
    )
}

function LoadingState() {
    return (
        <div className="h-screen w-full flex flex-col items-center justify-center bg-background gap-6">
            <div className="relative">
                <div className="w-20 h-20 wobbly-circle border-4 border-accent border-t-transparent animate-spin shadow-hand-md" />
                <Sparkles className="h-6 w-6 text-accent absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <div className="text-center space-y-2">
                <h2 className="font-heading text-xl text-foreground">Assembling your story...</h2>
                <p className="font-body text-foreground-subtle animate-pulse">Loading grounded CV data</p>
            </div>
        </div>
    )
}
