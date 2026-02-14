"use client";

import { useEffect, useState } from "react";
import { SketchCard } from "@/components/ui/hand-drawn";
import {
    Users, FileText, Briefcase, Cpu, TrendingUp,
    Activity, BarChart3, PieChart, Zap
} from "lucide-react";
import { cn } from "@/lib/utils";
import { getAnalytics, getSystemStatus, type PlatformAnalytics, type SystemStatus } from "@/lib/api/admin";

// ---- KPI Card ----

function KPICard({
    icon: Icon,
    label,
    value,
    subtitle,
    color,
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    value: string | number;
    subtitle?: string;
    color: string;
}) {
    const colorMap: Record<string, string> = {
        blue: "bg-ink-blue/10 text-ink-blue border-ink-blue/20",
        green: "bg-green-100 text-green-700 border-green-200",
        purple: "bg-purple-100 text-purple-700 border-purple-200",
        amber: "bg-amber-100 text-amber-700 border-amber-200",
        red: "bg-marker-red/10 text-marker-red border-marker-red/20",
    };

    return (
        <div className={cn("border-2 rounded-sm p-5 transition-all hover:shadow-md", colorMap[color] || colorMap.blue)}>
            <div className="flex items-center gap-3 mb-3">
                <Icon className="w-5 h-5" />
                <span className="text-sm font-handwritten uppercase tracking-wider opacity-70">{label}</span>
            </div>
            <p className="text-4xl font-marker">{value}</p>
            {subtitle && <p className="text-sm font-handwritten opacity-60 mt-1">{subtitle}</p>}
        </div>
    );
}

// ---- Tier Distribution Bar ----

function TierBar({ data }: { data: Record<string, number> }) {
    const total = Object.values(data).reduce((a, b) => a + b, 0);
    if (total === 0) return <p className="text-sm text-pencil-black/40 font-handwritten">No users yet</p>;

    const tierColors: Record<string, { bg: string; label: string }> = {
        free: { bg: "bg-gray-400", label: "Free" },
        plus: { bg: "bg-blue-500", label: "Plus" },
        pro: { bg: "bg-purple-500", label: "Pro" },
        premium: { bg: "bg-amber-500", label: "Premium" },
    };

    return (
        <div className="space-y-3">
            <div className="flex h-4 rounded-full overflow-hidden bg-gray-200">
                {Object.entries(data).map(([tier, count]) => (
                    count > 0 && (
                        <div
                            key={tier}
                            className={cn("transition-all", tierColors[tier]?.bg || "bg-gray-400")}
                            style={{ width: `${(count / total) * 100}%` }}
                            title={`${tierColors[tier]?.label || tier}: ${count}`}
                        />
                    )
                ))}
            </div>
            <div className="flex flex-wrap gap-4">
                {Object.entries(data).map(([tier, count]) => (
                    <div key={tier} className="flex items-center gap-2 text-sm font-handwritten">
                        <div className={cn("w-3 h-3 rounded-full", tierColors[tier]?.bg || "bg-gray-400")} />
                        <span className="capitalize font-bold">{tierColors[tier]?.label || tier}</span>
                        <span className="text-pencil-black/50">{count} ({Math.round((count / total) * 100)}%)</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ---- Status Badge ----

function StatusBadge({ label, value }: { label: string; value: boolean }) {
    return (
        <div className="flex items-center justify-between py-2 px-3 border rounded-sm">
            <span className="text-sm font-handwritten">{label}</span>
            <span className={cn(
                "text-xs font-bold uppercase px-2 py-0.5 rounded-full",
                value ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
            )}>
                {value ? "Active" : "Disabled"}
            </span>
        </div>
    );
}

// ---- Main Admin Dashboard ----

export default function AdminDashboardPage() {
    const [analytics, setAnalytics] = useState<PlatformAnalytics | null>(null);
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                const [analyticsData, statusData] = await Promise.allSettled([
                    getAnalytics(),
                    getSystemStatus(),
                ]);

                if (analyticsData.status === "fulfilled") setAnalytics(analyticsData.value);
                if (statusData.status === "fulfilled") setSystemStatus(statusData.value);

                if (analyticsData.status === "rejected" && statusData.status === "rejected") {
                    setError("Failed to load admin data. Are you an admin?");
                }
            } catch {
                setError("Failed to load admin data.");
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-10 w-10 border-4 border-dashed border-ink-blue mx-auto mb-3" />
                    <p className="text-lg font-handwritten text-pencil-black/50">Loading admin analytics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <p className="text-xl font-marker text-marker-red">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-4xl font-marker text-pencil-black mb-1">Platform Overview</h1>
                <p className="text-lg font-handwritten text-pencil-black/50">Real-time analytics and system status</p>
            </div>

            {/* ---- KPI Cards ---- */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <KPICard
                    icon={Users}
                    label="Total Users"
                    value={analytics?.total_users ?? 0}
                    subtitle={`+${analytics?.new_users_this_month ?? 0} this month`}
                    color="blue"
                />
                <KPICard
                    icon={Briefcase}
                    label="Applications"
                    value={analytics?.total_applications ?? 0}
                    subtitle={`${analytics?.applications_this_week ?? 0} this week`}
                    color="green"
                />
                <KPICard
                    icon={FileText}
                    label="Resumes"
                    value={analytics?.total_resumes ?? 0}
                    color="purple"
                />
                <KPICard
                    icon={Zap}
                    label="Agent Sessions"
                    value={analytics?.active_agent_sessions ?? 0}
                    subtitle="Currently active"
                    color="amber"
                />
            </div>

            {/* ---- User Tier Distribution ---- */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SketchCard className="p-6 hover:rotate-0">
                    <div className="flex items-center gap-2 mb-4">
                        <PieChart className="w-5 h-5 text-purple-600" />
                        <h2 className="text-2xl font-marker">User Distribution by Tier</h2>
                    </div>
                    {analytics?.users_by_tier && <TierBar data={analytics.users_by_tier} />}
                </SketchCard>

                <SketchCard className="p-6 hover:rotate-0">
                    <div className="flex items-center gap-2 mb-4">
                        <BarChart3 className="w-5 h-5 text-ink-blue" />
                        <h2 className="text-2xl font-marker">Applications by Status</h2>
                    </div>
                    {analytics?.applications_by_status && (
                        <div className="space-y-2">
                            {Object.entries(analytics.applications_by_status).map(([status, count]) => {
                                const maxCount = Math.max(...Object.values(analytics.applications_by_status));
                                const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                                return (
                                    <div key={status} className="flex items-center gap-3">
                                        <span className="w-24 text-sm font-handwritten capitalize text-right text-pencil-black/60">{status}</span>
                                        <div className="flex-1 h-6 bg-gray-100 rounded-sm overflow-hidden">
                                            <div
                                                className="h-full bg-ink-blue/60 rounded-sm transition-all"
                                                style={{ width: `${pct}%` }}
                                            />
                                        </div>
                                        <span className="w-10 text-sm font-marker text-right">{count}</span>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </SketchCard>
            </div>

            {/* ---- System Status ---- */}
            {systemStatus && (
                <SketchCard className="p-6 hover:rotate-0">
                    <div className="flex items-center gap-2 mb-5">
                        <Activity className="w-5 h-5 text-green-600" />
                        <h2 className="text-2xl font-marker">System Status</h2>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="border rounded-sm p-3">
                            <p className="text-xs font-handwritten text-pencil-black/50 uppercase">Environment</p>
                            <p className="text-xl font-marker capitalize">{systemStatus.environment}</p>
                        </div>
                        <div className="border rounded-sm p-3">
                            <p className="text-xs font-handwritten text-pencil-black/50 uppercase">AI Model</p>
                            <p className="text-xl font-marker">{systemStatus.ai_model}</p>
                        </div>
                        <div className="border rounded-sm p-3 col-span-full sm:col-span-2">
                            <p className="text-xs font-handwritten text-pencil-black/50 uppercase mb-2">Feature Flags</p>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                {Object.entries(systemStatus.features).map(([name, enabled]) => (
                                    <StatusBadge key={name} label={name.replace(/_/g, " ")} value={enabled} />
                                ))}
                            </div>
                        </div>
                    </div>
                </SketchCard>
            )}
        </div>
    );
}
