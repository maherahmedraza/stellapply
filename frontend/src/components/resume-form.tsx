"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { SketchButton, SketchCard, SketchInput } from "@/components/ui/hand-drawn";
import { Save, X, Sparkles, FileText, User, Mail, Phone, Info, Upload, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface ResumeFormProps {
    initialData?: any;
    resumeId?: string;
}

export function ResumeForm({ initialData, resumeId }: ResumeFormProps) {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [uploadMessage, setUploadMessage] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

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

    // Handle file upload
    const handleFileUpload = useCallback(async (file: File) => {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!validTypes.includes(file.type) && !file.name.endsWith('.docx') && !file.name.endsWith('.pdf')) {
            setUploadStatus('error');
            setUploadMessage('Please upload a PDF or DOCX file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            setUploadStatus('error');
            setUploadMessage('File size exceeds 10MB limit');
            return;
        }

        setUploading(true);
        setUploadStatus('idle');
        setUploadMessage('');

        try {
            const formDataUpload = new FormData();
            formDataUpload.append('file', file);

            const response = await api.post('/api/v1/resume/upload', formDataUpload, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            if (response.data.status === 'success') {
                const data = response.data.data;

                // Auto-fill the form with extracted data
                setPersonalInfo({
                    name: data.personal_info?.full_name || '',
                    email: data.personal_info?.email || '',
                    phone: data.personal_info?.phone || '',
                    summary: data.professional_summary || '',
                    location: data.personal_info?.location || '',
                });

                setFormData(prev => ({
                    ...prev,
                    name: `Resume - ${data.personal_info?.full_name || 'Imported'}`,
                    content: {
                        ...prev.content,
                        experience: data.experiences || [],
                        education: data.education || [],
                        skills: data.skills || [],
                    },
                }));

                setUploadStatus('success');
                setUploadMessage('Resume parsed successfully! Fields have been auto-filled.');
            }
        } catch (error: any) {
            console.error('Upload failed:', error);
            setUploadStatus('error');
            setUploadMessage(error.response?.data?.detail || 'Failed to parse resume. Please try again.');
        } finally {
            setUploading(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    }, [handleFileUpload]);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            if (resumeId) {
                await api.put(`/api/v1/resumes/${resumeId}`, formData);
            } else {
                await api.post("/api/v1/resumes", formData);
            }
            router.push("/dashboard/resumes");
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
            {/* Upload Section */}
            <SketchCard decoration="tape" className="p-8 rotate-0.5">
                <h2 className="text-3xl font-marker text-pencil-black mb-4 flex items-center gap-3">
                    <Upload className="w-8 h-8 text-ink-blue" />
                    Import Existing Resume
                </h2>
                <p className="font-handwritten text-lg text-pencil-black/70 mb-6">
                    Upload your PDF or DOCX resume and let AI auto-fill the form for you!
                </p>

                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onClick={() => fileInputRef.current?.click()}
                    className={`relative border-3 border-dashed p-8 text-center cursor-pointer transition-all wobble ${isDragging
                            ? 'border-ink-blue bg-ink-blue/10 scale-102'
                            : 'border-pencil-black/30 hover:border-pencil-black/60 hover:bg-muted-paper/30'
                        }`}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx,.doc"
                        onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                        className="hidden"
                    />

                    {uploading ? (
                        <div className="flex flex-col items-center gap-4">
                            <Loader2 className="w-12 h-12 text-ink-blue animate-spin" />
                            <span className="font-marker text-xl">Parsing with AI...</span>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-4">
                            <Upload className="w-12 h-12 text-pencil-black/40" />
                            <span className="font-marker text-xl">Drop your resume here</span>
                            <span className="font-handwritten text-sm text-pencil-black/60">
                                or click to browse (PDF, DOCX - max 10MB)
                            </span>
                        </div>
                    )}
                </div>

                {uploadStatus !== 'idle' && (
                    <div className={`mt-4 p-4 flex items-center gap-3 wobble ${uploadStatus === 'success'
                            ? 'bg-postit-green/20 border-2 border-pencil-black'
                            : 'bg-marker-red/10 border-2 border-marker-red'
                        }`}>
                        {uploadStatus === 'success'
                            ? <CheckCircle2 className="w-6 h-6 text-pencil-black" />
                            : <AlertCircle className="w-6 h-6 text-marker-red" />
                        }
                        <span className="font-handwritten text-lg">{uploadMessage}</span>
                    </div>
                )}
            </SketchCard>

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
