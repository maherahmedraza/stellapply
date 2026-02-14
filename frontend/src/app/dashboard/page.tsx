"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { SketchCard } from "@/components/ui/hand-drawn";
import {
  Rocket, FileText, Briefcase, UserCircle, Search, Star,
  TrendingUp, TrendingDown, Clock, CheckCircle2, XCircle,
  Send, AlertCircle, Zap, ChevronRight, Target,
  BarChart3, PieChart
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  getDashboardStats,
  getRecentApplications,
  getBillingInfo,
  getPersonaSummary,
  type ApplicationStats,
  type Application,
  type BillingInfo,
  type PersonaSummary,
} from "@/lib/api/dashboard";

// ---- Helpers ----

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function getStatusIcon(status: string) {
  switch (status?.toLowerCase()) {
    case "pending": return <Clock className="w-4 h-4" />;
    case "submitted": return <Send className="w-4 h-4" />;
    case "success": return <CheckCircle2 className="w-4 h-4" />;
    case "interviewing": return <Target className="w-4 h-4" />;
    case "failed":
    case "rejected": return <XCircle className="w-4 h-4" />;
    default: return <AlertCircle className="w-4 h-4" />;
  }
}

function getStatusStyle(status: string) {
  switch (status?.toLowerCase()) {
    case "pending": return "bg-postit-yellow/60 text-pencil-black border-yellow-600/30";
    case "submitted": return "bg-ink-blue/10 text-ink-blue border-ink-blue/30";
    case "success":
    case "offered": return "bg-green-100 text-green-800 border-green-300";
    case "interviewing": return "bg-purple-100 text-purple-800 border-purple-300";
    case "failed":
    case "rejected": return "bg-marker-red/10 text-marker-red border-marker-red/30";
    default: return "bg-gray-100 text-gray-600 border-gray-300";
  }
}

function getTierColor(tier: string) {
  switch (tier?.toLowerCase()) {
    case "free": return "bg-gray-200 text-gray-700 border-gray-400";
    case "plus": return "bg-blue-100 text-blue-800 border-blue-400";
    case "pro": return "bg-purple-100 text-purple-800 border-purple-400";
    case "premium": return "bg-gradient-to-r from-amber-200 to-yellow-300 text-amber-900 border-amber-500";
    default: return "bg-gray-200 text-gray-700 border-gray-400";
  }
}

// ---- Completeness Ring Component ----

function CompletenessRing({ value, size = 80 }: { value: number; size?: number }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const color = value >= 80 ? "#22c55e" : value >= 50 ? "#f59e0b" : value >= 20 ? "#f97316" : "#ef4444";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke="currentColor" className="text-pencil-black/10"
          strokeWidth="6" fill="none"
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke={color}
          strokeWidth="6" fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <span className="absolute text-lg font-marker">{Math.round(value)}%</span>
    </div>
  );
}

// ---- Stat Card Component ----

function StatCard({
  icon: Icon,
  label,
  value,
  subtitle,
  trend,
  color = "ink-blue",
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  color?: string;
}) {
  const colorMap: Record<string, string> = {
    "ink-blue": "bg-ink-blue/10 text-ink-blue",
    "green": "bg-green-100 text-green-700",
    "amber": "bg-amber-100 text-amber-700",
    "purple": "bg-purple-100 text-purple-700",
  };

  return (
    <SketchCard className="p-5 hover:rotate-0">
      <div className="flex items-start justify-between">
        <div className={cn("p-2.5 rounded-lg wobble", colorMap[color] || colorMap["ink-blue"])}>
          <Icon className="w-5 h-5" />
        </div>
        {trend && (
          <div className={cn("flex items-center gap-1 text-sm font-handwritten",
            trend === "up" ? "text-green-600" : trend === "down" ? "text-marker-red" : "text-gray-500"
          )}>
            {trend === "up" ? <TrendingUp className="w-4 h-4" /> : trend === "down" ? <TrendingDown className="w-4 h-4" /> : null}
          </div>
        )}
      </div>
      <div className="mt-3">
        <p className="text-3xl font-marker text-pencil-black">{value}</p>
        <p className="text-lg font-handwritten text-pencil-black/50 mt-0.5">{label}</p>
        {subtitle && (
          <p className="text-sm font-handwritten text-pencil-black/40 mt-1">{subtitle}</p>
        )}
      </div>
    </SketchCard>
  );
}

// ---- Quick Action Button ----

function QuickAction({
  href,
  icon: Icon,
  label,
  description,
  accent,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  description: string;
  accent: string;
}) {
  const accentMap: Record<string, string> = {
    blue: "bg-ink-blue text-white hover:bg-ink-blue/90",
    red: "bg-marker-red text-white hover:bg-marker-red/90",
    yellow: "bg-postit-yellow text-pencil-black hover:bg-postit-yellow/90",
    green: "bg-green-600 text-white hover:bg-green-700",
  };

  return (
    <Link href={href}>
      <div className={cn(
        "group wobble border-3 border-pencil-black p-5 shadow-sketch-sm transition-all",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        accentMap[accent] || accentMap.blue,
      )}>
        <div className="flex items-center gap-3">
          <Icon className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          <div>
            <p className="text-xl font-marker">{label}</p>
            <p className="text-sm font-handwritten opacity-80">{description}</p>
          </div>
          <ChevronRight className="w-5 h-5 ml-auto opacity-60 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}

// ---- Status Distribution Bar ----

function StatusBar({ stats }: { stats: Record<string, number> }) {
  const total = Object.values(stats).reduce((a, b) => a + b, 0);
  if (total === 0) return null;

  const colorMap: Record<string, string> = {
    pending: "bg-yellow-400",
    submitted: "bg-ink-blue",
    interviewing: "bg-purple-500",
    success: "bg-green-500",
    offered: "bg-green-500",
    failed: "bg-marker-red",
    rejected: "bg-marker-red",
  };

  return (
    <div className="space-y-2">
      <div className="flex h-3 rounded-full overflow-hidden border-2 border-pencil-black/20">
        {Object.entries(stats).map(([status, count]) => (
          count > 0 && (
            <div
              key={status}
              className={cn("transition-all", colorMap[status.toLowerCase()] || "bg-gray-400")}
              style={{ width: `${(count / total) * 100}%` }}
              title={`${status}: ${count}`}
            />
          )
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {Object.entries(stats).map(([status, count]) => (
          count > 0 && (
            <div key={status} className="flex items-center gap-1.5 text-sm font-handwritten text-pencil-black/60">
              <div className={cn("w-2.5 h-2.5 rounded-full", colorMap[status.toLowerCase()] || "bg-gray-400")} />
              <span className="capitalize">{status}</span>
              <span className="font-bold text-pencil-black">({count})</span>
            </div>
          )
        ))}
      </div>
    </div>
  );
}

// ---- Main Dashboard ----

export default function DashboardPage() {
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [recentApps, setRecentApps] = useState<Application[]>([]);
  const [billing, setBilling] = useState<BillingInfo | null>(null);
  const [persona, setPersona] = useState<PersonaSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAll() {
      try {
        const [statsData, appsData, billingData, personaData] = await Promise.allSettled([
          getDashboardStats(),
          getRecentApplications(),
          getBillingInfo(),
          getPersonaSummary(),
        ]);

        if (statsData.status === "fulfilled") setStats(statsData.value);
        if (appsData.status === "fulfilled") setRecentApps(appsData.value.items || []);
        if (billingData.status === "fulfilled") setBilling(billingData.value);
        if (personaData.status === "fulfilled") setPersona(personaData.value);
      } catch (err) {
        console.error("Dashboard load error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-dashed border-ink-blue mx-auto mb-4" />
          <p className="text-xl font-handwritten text-pencil-black/50">Loading your mission control...</p>
        </div>
      </div>
    );
  }

  const completeness = persona?.completeness_score ?? 0;
  const tier = billing?.current_plan?.tier_display || billing?.current_plan?.tier || "Free";
  const appLimit = billing?.usage?.application_limit;
  const appsUsed = billing?.usage?.applications_submitted ?? 0;

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500">

      {/* ======== Welcome Hero ======== */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          <CompletenessRing value={completeness} size={88} />
          <div>
            <h1 className="text-4xl md:text-5xl font-marker text-pencil-black flex items-center gap-3">
              Mission Control
              <Rocket className="w-9 h-9 text-ink-blue animate-bounce" />
            </h1>
            <p className="text-xl font-handwritten text-pencil-black/50 mt-1">
              {completeness < 40
                ? "Complete your persona to unlock AI matching!"
                : completeness < 80
                  ? "Good progress! Keep building your profile."
                  : "Your profile is stellar — ready for liftoff! 🚀"}
            </p>
          </div>
        </div>
        <div className={cn(
          "self-start wobble px-4 py-2 border-2 font-marker text-lg uppercase tracking-wider",
          getTierColor(billing?.current_plan?.tier || "free"),
        )}>
          <Star className="w-4 h-4 inline mr-1.5" />
          {tier} Plan
        </div>
      </div>

      {/* ======== Stats Strip ======== */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          icon={Briefcase}
          label="Total Applications"
          value={stats?.total ?? 0}
          subtitle={`${stats?.weekly_applied ?? 0} this week`}
          trend={stats?.weekly_applied && stats.weekly_applied > 0 ? "up" : "neutral"}
          color="ink-blue"
        />
        <StatCard
          icon={BarChart3}
          label="Response Rate"
          value={`${Math.round((stats?.response_rate ?? 0) * 100)}%`}
          subtitle={stats?.avg_time_to_response_days
            ? `~${Math.round(stats.avg_time_to_response_days)}d avg response`
            : "No responses yet"}
          trend={(stats?.response_rate ?? 0) > 0.2 ? "up" : "neutral"}
          color="green"
        />
        <StatCard
          icon={UserCircle}
          label="Persona Completeness"
          value={`${Math.round(completeness)}%`}
          subtitle={`${persona?.skills?.length ?? 0} skills · ${persona?.experiences?.length ?? 0} experiences`}
          color="purple"
        />
        <StatCard
          icon={Zap}
          label="Plan Usage"
          value={appLimit ? `${appsUsed}/${appLimit}` : `${appsUsed}`}
          subtitle={appLimit ? `${Math.max(0, appLimit - appsUsed)} applications remaining` : "Unlimited applications"}
          trend={appLimit && appsUsed >= appLimit ? "down" : "neutral"}
          color="amber"
        />
      </div>

      {/* ======== Application Status Distribution ======== */}
      {stats && Object.keys(stats.by_status).length > 0 && (
        <SketchCard className="p-5 hover:rotate-0">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="w-5 h-5 text-ink-blue" />
            <h2 className="text-2xl font-marker text-pencil-black">Application Pipeline</h2>
          </div>
          <StatusBar stats={stats.by_status} />
        </SketchCard>
      )}

      {/* ======== Quick Actions ======== */}
      <div>
        <h2 className="text-2xl font-marker text-pencil-black mb-4 -rotate-1">Quick Launch</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickAction
            href="/dashboard/jobs"
            icon={Search}
            label="Search Jobs"
            description="Find your next role"
            accent="blue"
          />
          <QuickAction
            href="/dashboard/resumes"
            icon={FileText}
            label="Build Resume"
            description="AI-powered resumes"
            accent="red"
          />
          <QuickAction
            href="/dashboard/persona"
            icon={UserCircle}
            label="My Persona"
            description={completeness < 50 ? "Complete your profile!" : "View & edit profile"}
            accent="yellow"
          />
          <QuickAction
            href="/dashboard/applications"
            icon={Send}
            label="Applications"
            description={`${stats?.total ?? 0} tracked`}
            accent="green"
          />
        </div>
      </div>

      {/* ======== Recent Activity ======== */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-marker text-pencil-black -rotate-1">Recent Activity</h2>
          {recentApps.length > 0 && (
            <Link
              href="/dashboard/applications"
              className="text-lg font-handwritten text-ink-blue hover:underline underline-offset-4 decoration-wavy flex items-center gap-1"
            >
              View all <ChevronRight className="w-4 h-4" />
            </Link>
          )}
        </div>

        {recentApps.length > 0 ? (
          <div className="space-y-3">
            {recentApps.map((app) => (
              <Link key={app.id} href={`/dashboard/applications/${app.id}`}>
                <SketchCard className="p-4 hover:rotate-0 hover:border-ink-blue transition-colors cursor-pointer">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 wobble bg-pencil-black/5 shrink-0">
                        <Briefcase className="w-4 h-4 text-pencil-black/50" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xl font-marker text-pencil-black truncate">
                          {app.job_title || "Untitled Position"}
                        </p>
                        <p className="text-base font-handwritten text-pencil-black/50 truncate">
                          {app.company_name || "Unknown Company"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-sm font-handwritten text-pencil-black/40">
                        {timeAgo(app.created_at)}
                      </span>
                      <span className={cn(
                        "wobble px-3 py-1 border-2 flex items-center gap-1.5 font-bold uppercase text-xs",
                        getStatusStyle(app.status),
                      )}>
                        {getStatusIcon(app.status)}
                        {app.status}
                      </span>
                    </div>
                  </div>
                </SketchCard>
              </Link>
            ))}
          </div>
        ) : (
          <SketchCard decoration="tape" className="py-16 flex flex-col items-center text-center">
            <Rocket className="w-16 h-16 text-pencil-black/10 mb-4 rotate-45" />
            <h3 className="text-2xl font-marker text-pencil-black mb-2">No missions launched yet</h3>
            <p className="text-lg font-handwritten text-pencil-black/40 max-w-md">
              Start by searching for jobs or building your AI-powered resume.
              Your applications will appear here once you begin!
            </p>
          </SketchCard>
        )}
      </div>
    </div>
  );
}
