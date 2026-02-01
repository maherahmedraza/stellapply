"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { Plus, FileText, Trash2, Edit, Pencil } from "lucide-react";
import { SketchButton, SketchCard } from "@/components/ui/hand-drawn";

export default function ResumesPage() {
    const [resumes, setResumes] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchResumes();
    }, []);

    const fetchResumes = async () => {
        try {
            const data = await api.get("/api/v1/resumes");
            setResumes(data || []);
        } catch (err) {
            console.error("Failed to fetch resumes", err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this sketch?")) return;
        try {
            await api.delete(`/api/v1/resumes/${id}`);
            fetchResumes();
        } catch (err) {
            alert("Failed to delete resume");
        }
    };

    if (loading)
        return (
            <div className="p-8 flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-8 w-8 border-4 border-dashed border-ink-blue"></div>
            </div>
        );

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6">
                <div>
                    <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">My Sketches</h1>
                    <p className="text-xl font-handwritten text-pencil-black/60">Manage and create your professional resumes.</p>
                </div>
                <Link href="/dashboard/resumes/new">
                    <SketchButton variant="accent" className="text-xl">
                        <Plus className="h-5 w-5 mr-2" strokeWidth={3} />
                        New Sketch
                    </SketchButton>
                </Link>
            </div>

            <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-3">
                {resumes.map((resume, i) => (
                    <SketchCard
                        key={resume.id}
                        decoration="tape"
                        className={i % 2 === 0 ? "rotate-1" : "-rotate-1"}
                    >
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center">
                                <div className="h-12 w-12 wobble bg-ink-blue/10 flex items-center justify-center text-ink-blue">
                                    <FileText className="h-6 w-6" strokeWidth={3} />
                                </div>
                                <div className="ml-4">
                                    <h3 className="text-2xl font-marker text-pencil-black truncate w-32">
                                        {resume.name}
                                    </h3>
                                    <p className="text-sm font-handwritten text-pencil-black/40">
                                        Updated {new Date(resume.updated_at).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                            {resume.is_primary && (
                                <span className="wobble px-2 py-1 bg-postit-yellow border border-pencil-black/20 text-xs font-bold uppercase rotate-3">
                                    Primary
                                </span>
                            )}
                        </div>

                        <div className="mt-auto flex gap-4">
                            <Link href={`/dashboard/resumes/${resume.id}`} className="flex-1">
                                <SketchButton variant="primary" className="w-full text-sm scale-90">
                                    <Edit className="h-4 w-4 mr-2" />
                                    Edit
                                </SketchButton>
                            </Link>
                            <button
                                onClick={() => handleDelete(resume.id)}
                                className="wobble p-3 border-2 border-pencil-black hover:bg-marker-red hover:text-white transition-colors shadow-sketch-sm active:shadow-none"
                            >
                                <Trash2 className="h-4 w-4" />
                            </button>
                        </div>
                    </SketchCard>
                ))}

                {resumes.length === 0 && (
                    <div className="col-span-full py-20 bg-muted-paper/20 rounded-3xl border-4 border-dashed border-pencil-black/20 flex flex-col items-center">
                        <Pencil className="h-20 w-20 text-pencil-black/20 mb-6 -rotate-12" />
                        <h3 className="text-3xl font-marker text-pencil-black mb-2">Blank canvas!</h3>
                        <p className="text-xl font-handwritten text-pencil-black/40 mb-8 text-center max-w-xs">
                            You haven't sketched any resumes yet. Start fresh or use a template.
                        </p>
                        <Link href="/dashboard/resumes/new">
                            <SketchButton variant="accent">Create Your First Sketch</SketchButton>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}
