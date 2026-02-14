"use client";

import { useEffect, useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Shield, Cpu, ToggleLeft, ToggleRight, Zap, Server, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import {
    getAIConfig, updateAIConfig, getSystemStatus, toggleFeature,
    type AIModelConfig, type SystemStatus
} from "@/lib/api/admin";

// ---- Feature Toggle ----

function FeatureToggle({
    name,
    enabled,
    onToggle,
    loading,
}: {
    name: string;
    enabled: boolean;
    onToggle: () => void;
    loading: boolean;
}) {
    const displayName = name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    return (
        <div className="flex items-center justify-between py-3 px-4 border-2 border-pencil-black/10 rounded-sm hover:border-pencil-black/20 transition-colors">
            <div>
                <p className="font-marker text-lg">{displayName}</p>
                <p className="text-sm font-handwritten text-pencil-black/40">
                    {enabled ? "Currently active" : "Currently disabled"}
                </p>
            </div>
            <button
                onClick={onToggle}
                disabled={loading}
                className={cn(
                    "p-1.5 rounded-sm transition-all",
                    enabled ? "text-green-600 hover:bg-green-50" : "text-gray-400 hover:bg-gray-50",
                    loading && "opacity-50"
                )}
            >
                {enabled ? (
                    <ToggleRight className="w-8 h-8" />
                ) : (
                    <ToggleLeft className="w-8 h-8" />
                )}
            </button>
        </div>
    );
}

// ---- Main Governance Page ----

export default function GovernancePage() {
    const [aiConfig, setAIConfig] = useState<AIModelConfig | null>(null);
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedModel, setSelectedModel] = useState<string>("");
    const [modelLoading, setModelLoading] = useState(false);
    const [featureLoading, setFeatureLoading] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                const [configData, statusData] = await Promise.allSettled([
                    getAIConfig(),
                    getSystemStatus(),
                ]);

                if (configData.status === "fulfilled") {
                    setAIConfig(configData.value);
                    setSelectedModel(configData.value.gemini_model);
                }
                if (statusData.status === "fulfilled") setSystemStatus(statusData.value);

                if (configData.status === "rejected" && statusData.status === "rejected") {
                    setError("Failed to load governance data. Admin access required.");
                }
            } catch {
                setError("Failed to load governance data.");
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const handleModelChange = async () => {
        if (!selectedModel || selectedModel === aiConfig?.gemini_model) return;
        setModelLoading(true);
        try {
            const updated = await updateAIConfig(selectedModel);
            setAIConfig(updated);
        } catch {
            alert("Failed to update AI model");
            setSelectedModel(aiConfig?.gemini_model || "");
        } finally {
            setModelLoading(false);
        }
    };

    const handleFeatureToggle = async (featureName: string) => {
        if (!systemStatus) return;
        const currentValue = systemStatus.features[featureName];
        setFeatureLoading(featureName);
        try {
            await toggleFeature(featureName, !currentValue);
            setSystemStatus({
                ...systemStatus,
                features: {
                    ...systemStatus.features,
                    [featureName]: !currentValue,
                },
            });
        } catch {
            alert("Failed to toggle feature");
        } finally {
            setFeatureLoading(null);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-10 w-10 border-4 border-dashed border-ink-blue mx-auto mb-3" />
                    <p className="text-lg font-handwritten text-pencil-black/50">Loading governance controls...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center p-6 bg-marker-red/10 border-2 border-marker-red/30 rounded-sm">
                    <AlertTriangle className="w-8 h-8 text-marker-red mx-auto mb-2" />
                    <p className="text-xl font-marker text-marker-red">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-4xl font-marker text-pencil-black mb-1 flex items-center gap-3">
                    <Shield className="w-8 h-8 text-marker-red" />
                    Governance Controls
                </h1>
                <p className="text-lg font-handwritten text-pencil-black/50">
                    System configuration, feature flags, and AI model management
                </p>
            </div>

            {/* ---- Feature Flags ---- */}
            <SketchCard className="p-6 hover:rotate-0">
                <div className="flex items-center gap-2 mb-5">
                    <Zap className="w-5 h-5 text-amber-600" />
                    <h2 className="text-2xl font-marker">Feature Flags</h2>
                </div>
                <p className="text-sm font-handwritten text-pencil-black/50 mb-4">
                    Toggle platform features in real-time. Changes take effect immediately.
                </p>
                <div className="space-y-2">
                    {systemStatus && Object.entries(systemStatus.features).map(([name, enabled]) => (
                        <FeatureToggle
                            key={name}
                            name={name}
                            enabled={enabled}
                            onToggle={() => handleFeatureToggle(name)}
                            loading={featureLoading === name}
                        />
                    ))}
                </div>
            </SketchCard>

            {/* ---- AI Model Configuration ---- */}
            <SketchCard className="p-6 hover:rotate-0">
                <div className="flex items-center gap-2 mb-5">
                    <Cpu className="w-5 h-5 text-ink-blue" />
                    <h2 className="text-2xl font-marker">AI Model Configuration</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-sm font-handwritten text-pencil-black/60 block mb-2">Generation Model</label>
                        <div className="flex gap-2">
                            <select
                                value={selectedModel}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                className="flex-1 border-2 border-pencil-black/20 px-3 py-2 text-base font-handwritten bg-white rounded-sm focus:border-ink-blue focus:outline-none"
                            >
                                {aiConfig?.available_models.map((model) => (
                                    <option key={model} value={model}>{model}</option>
                                ))}
                            </select>
                            <SketchButton
                                onClick={handleModelChange}
                                disabled={modelLoading || selectedModel === aiConfig?.gemini_model}
                                variant="primary"
                            >
                                {modelLoading ? "..." : "Apply"}
                            </SketchButton>
                        </div>
                        {selectedModel !== aiConfig?.gemini_model && (
                            <p className="text-xs text-amber-600 font-handwritten mt-1">
                                Unsaved change — click Apply to update
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="text-sm font-handwritten text-pencil-black/60 block mb-2">Embedding Model</label>
                        <div className="border-2 border-pencil-black/10 px-3 py-2 text-base font-handwritten bg-pencil-black/[0.02] rounded-sm">
                            {aiConfig?.embedding_model || "—"}
                        </div>
                    </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="border-2 border-pencil-black/10 p-3 rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Rate Limit</p>
                        <p className="text-2xl font-marker">{aiConfig?.rate_limit_rpm ?? "—"} <span className="text-sm font-handwritten text-pencil-black/40">req/min</span></p>
                    </div>
                    <div className="border-2 border-pencil-black/10 p-3 rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Active Model</p>
                        <p className="text-2xl font-marker">{aiConfig?.gemini_model ?? "—"}</p>
                    </div>
                </div>
            </SketchCard>

            {/* ---- System Info ---- */}
            <SketchCard className="p-6 hover:rotate-0">
                <div className="flex items-center gap-2 mb-4">
                    <Server className="w-5 h-5 text-pencil-black/60" />
                    <h2 className="text-2xl font-marker">System Information</h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 border rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Environment</p>
                        <p className="text-xl font-marker capitalize">{systemStatus?.environment}</p>
                    </div>
                    <div className="text-center p-3 border rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Total Users</p>
                        <p className="text-xl font-marker">{systemStatus?.total_users ?? 0}</p>
                    </div>
                    <div className="text-center p-3 border rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Applications</p>
                        <p className="text-xl font-marker">{systemStatus?.total_applications ?? 0}</p>
                    </div>
                    <div className="text-center p-3 border rounded-sm">
                        <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Agent Sessions</p>
                        <p className="text-xl font-marker">{systemStatus?.agent_sessions_active ?? 0}</p>
                    </div>
                </div>
            </SketchCard>

            {/* ---- Warning ---- */}
            <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-sm flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
                <div className="text-sm font-handwritten text-amber-800">
                    <p className="font-bold">Runtime Changes Only</p>
                    <p>Feature flag and AI model changes are applied to the running instance only. They will revert to .env defaults on restart. Update environment variables for persistent changes.</p>
                </div>
            </div>
        </div>
    );
}
