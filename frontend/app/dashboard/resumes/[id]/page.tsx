'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { ResumeForm } from '@/components/resume-form';
import { ResumePreview } from '@/components/resume-preview';
import clsx from 'clsx';

export default function EditResumePage() {
    const params = useParams();
    const id = params.id as string;
    const [resume, setResume] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (id) {
            fetchResume(id);
        }
    }, [id]);

    const fetchResume = async (resumeId: string) => {
        try {
            const data = await api.get(`/api/v1/resumes/${resumeId}`);
            setResume(data);
        } catch (err) {
            console.error('Failed to load resume', err);
        } finally {
            setLoading(false);
        }
    };

    const [analyzing, setAnalyzing] = useState(false);

    const handleAnalyze = async () => {
        if (!id) return;
        setAnalyzing(true);
        try {
            const result = await api.post(`/api/v1/resumes/${id}/analyze`, {});
            // The result is the updated resume object
            setResume(result);
        } catch (err) {
            console.error('Analysis failed', err);
            alert('Failed to analyze resume');
        } finally {
            setAnalyzing(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading editor...</div>;
    if (!resume) return <div className="p-8 text-center text-red-600">Resume not found</div>;

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Left Panel: Form */}
            <div className="w-1/2 overflow-y-auto border-r border-gray-200 bg-gray-50 p-6">
                <div className="mb-6">
                    <h1 className="text-xl font-bold text-gray-900">Editor</h1>
                    <p className="text-sm text-gray-500">Update your resume details</p>
                </div>
                <ResumeForm initialData={resume} resumeId={id} />
            </div>

            {/* Right Panel: Preview */}
            <div className="w-1/2 overflow-y-auto bg-gray-100 p-8 flex flex-col items-center">
                <div className="w-full max-w-[210mm] mb-4 flex justify-between items-center">
                    <h2 className="text-lg font-semibold text-gray-700">Preview</h2>
                    <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className={clsx(
                            "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white",
                            analyzing ? "bg-gray-400 cursor-not-allowed" : "bg-purple-600 hover:bg-purple-700 backdrop-blur-sm"
                        )}
                    >
                        {analyzing ? 'Analyzing...' : 'Analyze with AI'}
                    </button>
                </div>
                <div className="w-full max-w-[210mm]">
                    <ResumePreview data={resume} />
                </div>
            </div>
        </div>
    );
}
