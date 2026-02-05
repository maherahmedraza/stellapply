'use client'

import { useState, useCallback } from 'react'
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ResumePreview, ATSScoreCard, TemplateSelector } from './placeholders'
import { SectionEditor } from './section-editor'
import { AIEnhancementPanel } from './ai-enhancement-panel'
import { useTruthfulEnhancement } from '@/hooks/use-truthful-enhancement'
import { TruthfulEnhancementModal } from './truthful-enhancement-modal'

interface ResumeBuilderProps {
    resumeId?: string
    initialData?: unknown
}

export function ResumeBuilder({ resumeId }: ResumeBuilderProps) {
    void resumeId;
    const [activeTab, setActiveTab] = useState('edit')
    const [selectedSection, setSelectedSection] = useState<string | null>(null)
    const [showAIPanel, setShowAIPanel] = useState(false)

    // New Truthful Enhancer Hook
    const { enhance, enhancement, clearEnhancement, isLoading: isTruthfulLoading } = useTruthfulEnhancement()

    const {
        resume,
        sections,
        atsScore,
        isEnhancing,
        updateSection,
        reorderSections,
        enhanceWithAI, // Legacy store method
        analyzeATS,
        downloadResume,
        updateResume
    } = useResumeStore()

    const handleDragEnd = useCallback((event: DragEndEvent) => {
        const { active, over } = event
        if (over && active.id !== over.id) {
            reorderSections(active.id as string, over.id as string)
        }
    }, [reorderSections])

    const handleEnhanceSection = async (sectionId: string) => {
        // setShowAIPanel(true) // Disable old panel
        setSelectedSection(sectionId)

        const section = sections.find(s => s.id === sectionId)
        if (!section) return

        let contentToEnhance = ""
        if (section.type === 'summary') {
            contentToEnhance = section.content as string
        } else if (section.type === 'experience') {
            const exps = section.content as any[]
            // For demo, picking first achievement
            contentToEnhance = exps?.[0]?.achievements?.[0] || exps?.[0]?.description || ""
        }

        if (contentToEnhance) {
            await enhance(contentToEnhance)
        }
    }

    return (
        <div className="flex h-full gap-6 p-6">
            {/* Left Panel - Editor */}
            <div className="flex-1 flex flex-col max-w-2xl">
                <div className="flex items-center justify-between mb-4">
                    <h1 className="text-2xl font-bold">Resume Builder</h1>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => analyzeATS()}
                            className="gap-2"
                        >
                            <BarChart2 className="h-4 w-4" />
                            Check ATS Score
                        </Button>
                        <Button
                            onClick={() => setShowAIPanel(true)}
                            className="gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700"
                        >
                            <Sparkles className="h-4 w-4" />
                            AI Enhance
                        </Button>
                    </div>
                </div>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="edit" className="gap-2">
                            <FileText className="h-4 w-4" />
                            Edit
                        </TabsTrigger>
                        <TabsTrigger value="template" className="gap-2">
                            <Eye className="h-4 w-4" />
                            Template
                        </TabsTrigger>
                        <TabsTrigger value="ats" className="gap-2">
                            <BarChart2 className="h-4 w-4" />
                            ATS Analysis
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="edit" className="flex-1 overflow-auto">
                        <DndContext
                            collisionDetection={closestCenter}
                            onDragEnd={handleDragEnd}
                        >
                            <SortableContext
                                items={sections.map(s => s.id)}
                                strategy={verticalListSortingStrategy}
                            >
                                <div className="space-y-4 py-4">
                                    {sections.map((section) => (
                                        <SectionEditor
                                            key={section.id}
                                            section={section}
                                            onUpdate={(data) => updateSection(section.id, data)}
                                            onEnhance={() => handleEnhanceSection(section.id)}
                                            isEnhancing={(isEnhancing || isTruthfulLoading) && selectedSection === section.id}
                                        />
                                    ))}
                                </div>
                            </SortableContext>
                        </DndContext>
                    </TabsContent>

                    <TabsContent value="template">
                        <TemplateSelector
                            currentTemplate={resume?.templateId}
                            onSelect={(templateId) => updateResume({ templateId })}
                        />
                    </TabsContent>

                    <TabsContent value="ats">
                        <ATSScoreCard
                            score={atsScore}
                            onReanalyze={analyzeATS}
                        />
                    </TabsContent>
                </Tabs>
            </div>

            {/* Right Panel - Preview */}
            <div className="flex-1 flex flex-col border rounded-lg bg-white dark:bg-gray-800 overflow-hidden shadow-sm">
                <div className="flex items-center justify-between p-4 border-b bg-gray-50 dark:bg-gray-900/50">
                    <h2 className="font-semibold">Preview</h2>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadResume('pdf')}
                        >
                            <Download className="h-4 w-4 mr-2" />
                            PDF
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadResume('docx')}
                        >
                            <Download className="h-4 w-4 mr-2" />
                            DOCX
                        </Button>
                    </div>
                </div>

                <div className="flex-1 overflow-auto p-4 bg-gray-100 dark:bg-gray-900">
                    <ResumePreview
                        resume={resume}
                        sections={sections}
                        template={resume?.templateId}
                    />
                </div>
            </div>

            {/* AI Enhancement Slide-over Panel (Legacy/Alternative) */}
            <AIEnhancementPanel
                open={showAIPanel}
                onClose={() => setShowAIPanel(false)}
                section={sections.find(s => s.id === selectedSection)}
                onApplySuggestion={(text) => {
                    // ... existing logic ...
                }}
            />

            {/* New Truthful Enhancement Modal */}
            {enhancement && (
                <TruthfulEnhancementModal
                    enhancement={enhancement}
                    onAccept={(text) => {
                        if (selectedSection) {
                            const section = sections.find(s => s.id === selectedSection)
                            if (!section) return

                            if (section.type === 'summary') {
                                updateSection(selectedSection, { content: text })
                            } else if (section.type === 'experience') {
                                const experiences = section.content as any[]
                                if (experiences && experiences.length > 0) {
                                    const newExperiences = JSON.parse(JSON.stringify(experiences))
                                    if (newExperiences[0].achievements && newExperiences[0].achievements.length > 0) {
                                        newExperiences[0].achievements[0] = text
                                    } else {
                                        newExperiences[0].description = text
                                    }
                                    updateSection(selectedSection, { content: newExperiences })
                                }
                            }
                        }
                        clearEnhancement()
                    }}
                    onReject={clearEnhancement}
                    onVerify={() => { }}
                />
            )}
        </div>
    )
}
