import { ResumeData, ResumeSection } from "@/stores/resume.store";

export function ResumePreview({ resume }: { resume: ResumeData | null, sections: ResumeSection[], template: string | undefined }) {
    if (!resume) return <div>No resume data</div>;
    return (
        <div className="prose max-w-none p-8 bg-white min-h-[800px] shadow-lg">
            <h1 className="text-3xl font-bold">{resume.title}</h1>
            <pre className="text-xs mt-4 overflow-auto">{JSON.stringify(resume, null, 2)}</pre>
        </div>
    );
}

export function ATSScoreCard({ score, onReanalyze }: { score: number, onReanalyze: () => void }) {
    return (
        <div className="p-4 border rounded-lg">
            <h3 className="font-bold">ATS Score: {score}/100</h3>
            <button onClick={onReanalyze} className="text-blue-500 hover:underline">Reanalyze</button>
        </div>
    )
}

export function TemplateSelector({ currentTemplate, onSelect }: { currentTemplate: string | undefined, onSelect: (id: string) => void }) {
    return (
        <div className="grid grid-cols-2 gap-4">
            {['modern', 'classic', 'minimal'].map(t => (
                <div
                    key={t}
                    className={`p-4 border rounded cursor-pointer ${currentTemplate === t ? 'ring-2 ring-primary' : ''}`}
                    onClick={() => onSelect(t)}
                >
                    {t}
                </div>
            ))}
        </div>
    )
}
