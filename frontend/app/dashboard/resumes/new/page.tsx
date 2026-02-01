'use client';

import { ResumeForm } from '@/components/resume-form';

export default function NewResumePage() {
    return (
        <div className="p-8 max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">Create New Resume</h1>
                <p className="text-gray-500">Start building your professional profile.</p>
            </div>
            <ResumeForm />
        </div>
    );
}
