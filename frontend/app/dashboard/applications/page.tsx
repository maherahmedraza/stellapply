"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Briefcase, Clock, CheckCircle2, XCircle, AlertCircle, ExternalLink, Eraser } from "lucide-react";
import { cn } from "@/lib/utils";
import { SketchCard } from "@/components/ui/hand-drawn";

export default function ApplicationsPage() {
    const [applications, setApplications] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchApplications();
    }, []);

    const fetchApplications = async () => {
        try {
            const data = await api.get("/api/v1/applications");
            setApplications(data || []);
        } catch (err) {
            console.error("Failed to fetch applications", err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case "pending": return "bg-postit-yellow text-pencil-black border-pencil-black/20";
            case "submitted": return "bg-ink-blue/10 text-ink-blue border-ink-blue/20";
            case "success": return "bg-green-100 text-green-800 border-green-200";
            case "failed": return "bg-marker-red/10 text-marker-red border-marker-red/20";
            default: return "bg-muted-paper text-pencil-black border-pencil-black/20";
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status.toLowerCase()) {
            case "pending": return <Clock className="h-4 w-4" />;
            case "submitted": return <ExternalLink className="h-4 w-4" />;
            case "success": return <CheckCircle2 className="h-4 w-4" />;
            case "failed": return <XCircle className="h-4 w-4" />;
            default: return <AlertCircle className="h-4 w-4" />;
        }
    };

    if (loading)
        return (
            <div className="p-8 flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-8 w-8 border-4 border-dashed border-ink-blue"></div>
            </div>
        );

    return (
        <div className="p-8 max-w-5xl mx-auto animate-in fade-in duration-700">
            <div className="mb-12">
                <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Application Track</h1>
                <p className="text-xl font-handwritten text-pencil-black/60">Monitor your automated job journey.</p>
            </div>

            <div className="grid gap-8">
                {applications.map((app, i) => (
                    <SketchCard
                        key={app.id}
                        decoration={i === 0 ? "tack" : "none"}
                        className={cn("flex flex-col md:flex-row md:items-center justify-between gap-6", i % 2 === 0 ? "rotate-0.5" : "-rotate-0.5")}
                    >
                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 wobble bg-pencil-black/5">
                                    <Briefcase className="w-5 h-5 text-pencil-black/60" />
                                </div>
                                <h3 className="text-2xl font-marker text-pencil-black">Full Stack Engineer (Placeholder)</h3>
                            </div>
                            <div className="flex flex-wrap gap-4 text-lg font-handwritten text-pencil-black/60">
                                <span className="font-bold text-pencil-black">TechCorp Inc.</span>
                                <span>•</span>
                                <span>Applied via {app.submission_mode || "Automated"}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="text-right hidden md:block">
                                <div className="text-sm font-handwritten text-pencil-black/40 uppercase tracking-widest">Submitted</div>
                                <div className="text-lg font-bold">
                                    {app.submitted_at
                                        ? new Date(app.submitted_at).toLocaleDateString()
                                        : "TBD"}
                                </div>
                            </div>

                            <div className={cn(
                                "wobble px-4 py-2 border-2 flex items-center gap-2 font-bold uppercase text-sm shadow-sketch-sm",
                                getStatusColor(app.status)
                            )}>
                                {getStatusIcon(app.status)}
                                {app.status}
                            </div>
                        </div>
                    </SketchCard>
                ))}

                {applications.length === 0 && (
                    <div className="py-24 bg-white wobble-md border-[3px] border-pencil-black border-dashed flex flex-col items-center">
                        <Eraser className="w-20 h-20 text-pencil-black/10 mb-6 rotate-12" />
                        <h3 className="text-3xl font-marker text-pencil-black mb-2">No applications yet</h3>
                        <p className="text-xl font-handwritten text-pencil-black/40 text-center max-w-md">
                            When our workers apply to jobs for you, they will appear here as sketched cards.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
