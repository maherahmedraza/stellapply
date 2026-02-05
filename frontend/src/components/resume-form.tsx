"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { SketchButton, SketchCard, SketchInput } from "@/components/ui/hand-drawn";
import { Save, X, Sparkles, FileText, User, Mail, Phone, Info } from "lucide-react";

interface ResumeFormProps {
    initialData?: any;
    resumeId?: string;
}

export function ResumeForm({ initialData, resumeId }: ResumeFormProps) {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: initialData?.name || "",
        template_id: initialData?.template_id || "modern_v1",
        is_primary: initialData?.is_primary || false,
        content: initialData?.content || {
            personal_info: { name: "", email: "", phone: "", summary: "" },
            experience: [],
            education: [],
            skills: [],
        },
    });

    const [personalInfo, setPersonalInfo] = useState(formData.content.personal_info || {});

    useEffect(() => {
        setFormData((prev) => ({
            ...prev,
            content: {
                ...prev.content,
                personal_info: personalInfo,
            },
        }));
    }, [personalInfo]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            let id = resumeId;
            if (resumeId) {
                await api.put(`/api/v1/resume/${resumeId}`, formData);
            } else {
                const res = await api.post("/api/v1/resume", formData);
                id = res.id;
            }
            router.push(`/dashboard/resumes/${id}`);
            router.refresh();
        } catch (error) {
            console.error("Failed to save resume:", error);
            alert("Failed to save sketch");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-12 pb-20">
            <div className="flex flex-col md:flex-row gap-8">
                <div className="flex-1 space-y-8">
                    <SketchCard decoration="none" className="rotate-0.5 shadow-sketch-lg p-8">
                        <h2 className="text-3xl font-marker text-pencil-black mb-6 flex items-center gap-3">
                            <FileText className="w-8 h-8 text-ink-blue" />
                            General Info
                        </h2>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Sketch Name</label>
                                <SketchInput
                                    type="text"
                                    placeholder="e.g. Senior Dev 2026"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full text-lg"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Visual Style</label>
                                <div className="grid grid-cols-3 gap-4">
                                    {["modern_v1", "classic", "minimal"].map((t) => (
                                        <button
                                            key={t}
                                            type="button"
                                            onClick={() => setFormData({ ...formData, template_id: t })}
                                            className={`wobble px-4 py-2 border-2 font-handwritten font-bold capitalize transition-all ${formData.template_id === t
                                                ? "bg-ink-blue text-white border-pencil-black shadow-sketch-sm rotate-2"
                                                : "bg-white text-pencil-black/40 border-pencil-black/20 hover:border-pencil-black/40"
                                                }`}
                                        >
                                            {t.replace("_v1", "")}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex items-center gap-4 py-4 bg-muted-paper/5 border-y border-dashed border-pencil-black/10">
                                <input
                                    type="checkbox"
                                    checked={formData.is_primary}
                                    onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                                    id="is_primary"
                                    className="w-6 h-6 wobble accent-ink-blue border-2 border-pencil-black cursor-pointer"
                                />
                                <label htmlFor="is_primary" className="text-xl font-handwritten font-bold cursor-pointer">
                                    Set as my primary sketch
                                </label>
                            </div>
                        </div>
                    </SketchCard>

                    <SketchCard decoration="tack" className="-rotate-0.5 shadow-sketch-lg p-8">
                        <h2 className="text-3xl font-marker text-pencil-black mb-6 flex items-center gap-3">
                            <User className="w-8 h-8 text-marker-red" />
                            Personal Details
                        </h2>

                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-xl font-bold mb-2 ml-2">Full Name</label>
                                    <div className="relative">
                                        <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                        <SketchInput
                                            type="text"
                                            placeholder="Leonardo"
                                            value={personalInfo.name || ""}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, name: e.target.value })}
                                            className="pl-12 w-full"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xl font-bold mb-2 ml-2">Email</label>
                                    <div className="relative">
                                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                        <SketchInput
                                            type="email"
                                            placeholder="leo@draw.ai"
                                            value={personalInfo.email || ""}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, email: e.target.value })}
                                            className="pl-12 w-full"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Phone</label>
                                <div className="relative">
                                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                    <SketchInput
                                        type="text"
                                        placeholder="+1 234 567"
                                        value={personalInfo.phone || ""}
                                        onChange={(e) => setPersonalInfo({ ...personalInfo, phone: e.target.value })}
                                        className="pl-12 w-full"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Professional Summary</label>
                                <textarea
                                    value={personalInfo.summary || ""}
                                    onChange={(e) => setPersonalInfo({ ...personalInfo, summary: e.target.value })}
                                    placeholder="I draw pixels and solve puzzles..."
                                    rows={4}
                                    className="w-full bg-white wobble border-2 border-pencil-black p-4 text-xl font-handwritten focus:outline-none focus:ring-4 focus:ring-ink-blue/10 transition-all resize-none shadow-sketch-sm"
                                />
                            </div>
                        </div>
                    </SketchCard>
                </div>

                <div className="md:w-64 space-y-6">
                    <div className="sticky top-24 space-y-6">
                        <SketchButton variant="accent" type="submit" disabled={loading} className="w-full py-6 text-2xl rotate-2">
                            {loading ? "Saving..." : "Save Sketch"}
                            <Save className="ml-2 w-6 h-6" strokeWidth={3} />
                        </SketchButton>

                        <SketchButton variant="primary" type="button" onClick={() => router.back()} className="w-full py-4 text-xl -rotate-1">
                            Cancel
                            <X className="ml-2 w-5 h-5" />
                        </SketchButton>

                        <div className="p-6 wobble bg-postit-yellow/20 border-2 border-pencil-black border-dashed rotate-1 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1 bg-marker-red opacity-20"></div>
                            <h4 className="font-marker text-lg flex items-center gap-2 mb-2">
                                <Info className="w-5 h-5 text-marker-red" />
                                Doodle Tip
                            </h4>
                            <p className="font-handwritten text-lg leading-tight text-pencil-black/70">
                                AI loves clean sketches! Make sure your summary is punchy.
                            </p>
                            <div className="absolute -bottom-4 -right-4 opacity-10 rotate-12">
                                <Sparkles className="w-16 h-16" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    );
}
