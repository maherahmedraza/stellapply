'use client';

import { useParams } from 'next/navigation';
import { ResumeBuilder } from '@/components/resume/resume-builder';

export default function EditResumePage() {
    const params = useParams();
    const id = params.id as string;

    return (
        <div className="bg-background h-[calc(100vh-4rem)]">
            <ResumeBuilder resumeId={id} />
        </div>
    );
}
