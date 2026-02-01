'use client'

import { useState } from 'react'
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Sparkles, Check, RefreshCw, ArrowRight } from 'lucide-react'
import { useAIEnhancement } from '@/hooks/use-ai-enhancement'
import { ResumeSection } from '@/stores/resume.store'
import { cn } from '@/lib/utils'

interface AIEnhancementPanelProps {
    open: boolean
    onClose: () => void
    section: ResumeSection | undefined
    onApplySuggestion: (suggestion: string) => void
}

export function AIEnhancementPanel({
    open,
    onClose,
    section,
    onApplySuggestion,
}: AIEnhancementPanelProps) {
    const [activeTab, setActiveTab] = useState('suggestions')

    const {
        suggestions,
        isLoading,
        regenerate,
        appliedSuggestions,
        markAsApplied,
    } = useAIEnhancement(section?.id)

    return (
        <Sheet open={open} onOpenChange={onClose}>
            <SheetContent className="w-[500px] sm:max-w-[500px]">
                <SheetHeader>
                    <SheetTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-500" />
                        AI Enhancement
                    </SheetTitle>
                    <SheetDescription>
                        Review AI-generated improvements for your {section?.title.toLowerCase()}
                    </SheetDescription>
                </SheetHeader>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
                        <TabsTrigger value="keywords">Keywords</TabsTrigger>
                        <TabsTrigger value="metrics">Add Metrics</TabsTrigger>
                    </TabsList>

                    <TabsContent value="suggestions" className="mt-4">
                        <ScrollArea className="h-[calc(100vh-250px)]">
                            <div className="space-y-4 pr-4">
                                {isLoading ? (
                                    <div className="flex items-center justify-center py-12">
                                        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
                                    </div>
                                ) : (
                                    suggestions.map((suggestion, index) => (
                                        <Card
                                            key={index}
                                            className={cn(
                                                'transition-all',
                                                appliedSuggestions.includes(index) && 'border-green-500 bg-green-50'
                                            )}
                                        >
                                            <CardContent className="p-4 space-y-3">
                                                <div className="space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <Badge variant="outline">Original</Badge>
                                                    </div>
                                                    <p className="text-sm text-gray-600">{suggestion.original}</p>
                                                </div>

                                                <ArrowRight className="h-4 w-4 text-gray-400 mx-auto" />

                                                <div className="space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <Badge className="bg-purple-100 text-purple-700">Enhanced</Badge>
                                                        {suggestion.metricsAdded && (
                                                            <Badge variant="secondary">+Metrics</Badge>
                                                        )}
                                                    </div>
                                                    <p className="text-sm font-medium">{suggestion.enhanced}</p>
                                                </div>

                                                <div className="flex justify-end gap-2 pt-2">
                                                    {appliedSuggestions.includes(index) ? (
                                                        <Button variant="ghost" size="sm" disabled>
                                                            <Check className="h-4 w-4 mr-1" />
                                                            Applied
                                                        </Button>
                                                    ) : (
                                                        <Button
                                                            size="sm"
                                                            onClick={() => {
                                                                onApplySuggestion(suggestion.enhanced)
                                                                markAsApplied(index)
                                                            }}
                                                        >
                                                            Apply
                                                        </Button>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                )}
                            </div>
                        </ScrollArea>

                        <div className="pt-4 border-t mt-4">
                            <Button
                                variant="outline"
                                onClick={regenerate}
                                disabled={isLoading}
                                className="w-full gap-2"
                            >
                                <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
                                Generate More Suggestions
                            </Button>
                        </div>
                    </TabsContent>

                    <TabsContent value="keywords">
                        <div className="p-4 text-center text-muted-foreground">
                            Keyword optimization coming soon.
                        </div>
                    </TabsContent>

                    <TabsContent value="metrics">
                        <div className="p-4 text-center text-muted-foreground">
                            Metrics suggestions coming soon.
                        </div>
                    </TabsContent>
                </Tabs>
            </SheetContent>
        </Sheet>
    )
}
