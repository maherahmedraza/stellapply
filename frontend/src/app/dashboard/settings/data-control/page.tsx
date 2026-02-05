"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Shield, Download, Trash2, AlertTriangle, CloudOff } from "lucide-react";
import { api } from "@/lib/api";

export default function PrivacySettingsPage() {
    const [isDeleting, setIsDeleting] = useState(false);
    const [isRestricted, setIsRestricted] = useState(false);

    const handleExport = async () => {
        try {
            // Re-use API logic but trigger download
            const response = await fetch('/api/v1/privacy/export');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "stellapply_data_export.json";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            alert("Failed to export data. Please try again.");
        }
    };

    const toggleRestriction = async () => {
        try {
            await api.put('/api/v1/privacy/restrict', { restricted: !isRestricted });
            setIsRestricted(!isRestricted);
        } catch (err) {
            alert("Failed to update processing restriction.");
        }
    };

    const handleDelete = async () => {
        if (!confirm("Are you ABSOLUTELY sure? This will schedule your account for permanent deletion in 30 days.")) {
            return;
        }

        setIsDeleting(true);
        try {
            await api.delete('/api/v1/privacy/delete');
            alert("Account scheduled for deletion. You will be logged out.");
            window.location.href = "/";
        } catch (err) {
            alert("Failed to delete account.");
            setIsDeleting(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
            <header className="mb-12">
                <h1 className="text-5xl font-handwritten text-pencil-black mb-4">Privacy & Data Sketches</h1>
                <p className="text-xl font-body text-pencil-black/70">
                    Your data, your rules. Sketch out your privacy preferences.
                </p>
            </header>

            <div className="grid gap-8">
                {/* Data Portability */}
                <SketchCard decoration="tape" className="space-y-4">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-ink-blue/10 rounded-full">
                            <Download className="w-8 h-8 text-ink-blue" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-handwritten text-pencil-black mb-2">Right to Access (GDPR Article 15)</h2>
                            <p className="text-pencil-black/70 mb-4">
                                Download a complete copy of all your sketches, personas, and applications in a machine-readable format.
                            </p>
                            <SketchButton onClick={handleExport} variant="primary">
                                Export My Data (.JSON)
                            </SketchButton>
                        </div>
                    </div>
                </SketchCard>

                {/* Processing Restriction */}
                <SketchCard decoration="none" className="space-y-4 border-dashed">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-postit-yellow/20 rounded-full">
                            <CloudOff className="w-8 h-8 text-pencil-black" />
                        </div>
                        <div className="flex-1">
                            <h2 className="text-2xl font-handwritten text-pencil-black mb-2">Restrict Processing</h2>
                            <p className="text-pencil-black/70 mb-4">
                                Pause AI profiling and automated job matching. Your data will be kept but no new matches will be generated.
                            </p>
                            <div className="flex items-center gap-4">
                                <SketchButton
                                    onClick={toggleRestriction}
                                    variant={isRestricted ? "accent" : "secondary"}
                                >
                                    {isRestricted ? "Resume Processing" : "Pause AI Processing"}
                                </SketchButton>
                                {isRestricted && (
                                    <span className="text-marker-red font-bold animate-pulse">
                                        Processing Restricted
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                </SketchCard>

                {/* Erasure */}
                <SketchCard decoration="none" className="bg-white border-marker-red border-[4px]">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-marker-red/10 rounded-full">
                            <Trash2 className="w-8 h-8 text-marker-red" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-handwritten text-marker-red mb-2">Right to Erasure</h2>
                            <p className="text-pencil-black/70 mb-4 text-sm italic">
                                Article 17: The Right to be Forgotten.
                            </p>
                            <p className="text-pencil-black/70 mb-6 font-bold">
                                Deleting your account is permanent. All your resumes, applications, and persona data will be wiped after a 30-day grace period.
                            </p>
                            <SketchButton
                                onClick={handleDelete}
                                variant="accent"
                                disabled={isDeleting}
                            >
                                {isDeleting ? "Shredding..." : "Delete My Account Forever"}
                            </SketchButton>
                        </div>
                    </div>
                </SketchCard>

                {/* Legal Basis Info */}
                <div className="p-6 bg-pencil-black text-white wobble-md text-sm font-body">
                    <p className="flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Data Controller: StellarApply GmbH | Processing Location: EU (Germany)
                    </p>
                    <p className="mt-2 text-white/60">
                        Legal Basis: Article 6(1)(b) - Contractual necessity for providing automated career assistance.
                    </p>
                </div>
            </div>
        </div>
    );
}
