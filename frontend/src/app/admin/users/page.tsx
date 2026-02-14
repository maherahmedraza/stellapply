"use client";

import { useEffect, useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Users, Search, ChevronLeft, ChevronRight, Shield, AlertTriangle, } from "lucide-react";
import { cn } from "@/lib/utils";
import { getUsers, updateUser, type AdminUser, type AdminUserListResponse } from "@/lib/api/admin";

// ---- Tier Badge ----

function TierBadge({ tier }: { tier: string }) {
    const styles: Record<string, string> = {
        free: "bg-gray-200 text-gray-700",
        plus: "bg-blue-100 text-blue-800",
        pro: "bg-purple-100 text-purple-800",
        premium: "bg-gradient-to-r from-amber-200 to-yellow-300 text-amber-900",
    };

    return (
        <span className={cn(
            "px-2.5 py-0.5 text-xs font-bold uppercase rounded-full border",
            styles[tier.toLowerCase()] || styles.free,
        )}>
            {tier}
        </span>
    );
}

// ---- Status Badge ----

function UserStatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        active: "bg-green-100 text-green-800 border-green-300",
        suspended: "bg-amber-100 text-amber-800 border-amber-300",
        banned: "bg-red-100 text-red-800 border-red-300",
    };

    return (
        <span className={cn(
            "px-2 py-0.5 text-xs font-bold uppercase rounded-sm border",
            styles[status.toLowerCase()] || styles.active,
        )}>
            {status}
        </span>
    );
}

// ---- Main Users Page ----

export default function AdminUsersPage() {
    const [data, setData] = useState<AdminUserListResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [tierFilter, setTierFilter] = useState<string>("");
    const [statusFilter, setStatusFilter] = useState<string>("");
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    const perPage = 15;

    const fetchUsers = async (p: number = page) => {
        setLoading(true);
        try {
            const result = await getUsers({
                page: p,
                per_page: perPage,
                tier: tierFilter || undefined,
                status: statusFilter || undefined,
            });
            setData(result);
            setError(null);
        } catch {
            setError("Failed to load users. Admin access required.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers(page);
    }, [page, tierFilter, statusFilter]);

    const handleTierChange = async (userId: string, newTier: string) => {
        setActionLoading(userId);
        try {
            await updateUser(userId, { tier: newTier });
            await fetchUsers(page);
        } catch {
            alert("Failed to update user tier");
        } finally {
            setActionLoading(null);
        }
    };

    const handleStatusChange = async (userId: string, newStatus: string) => {
        if (newStatus === "banned" && !confirm("Are you sure you want to ban this user?")) return;
        setActionLoading(userId);
        try {
            await updateUser(userId, { status: newStatus });
            await fetchUsers(page);
        } catch {
            alert("Failed to update user status");
        } finally {
            setActionLoading(null);
        }
    };

    const totalPages = data ? Math.ceil(data.total / perPage) : 0;

    return (
        <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
            <div>
                <h1 className="text-4xl font-marker text-pencil-black mb-1 flex items-center gap-3">
                    <Users className="w-8 h-8 text-ink-blue" />
                    User Management
                </h1>
                <p className="text-lg font-handwritten text-pencil-black/50">
                    {data ? `${data.total} users total` : "Loading..."}
                </p>
            </div>

            {/* ---- Filters ---- */}
            <div className="flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2">
                    <label className="text-sm font-handwritten text-pencil-black/60">Tier:</label>
                    <select
                        value={tierFilter}
                        onChange={(e) => { setTierFilter(e.target.value); setPage(1); }}
                        className="border-2 border-pencil-black/20 px-3 py-1.5 text-sm font-handwritten bg-white rounded-sm focus:border-ink-blue focus:outline-none"
                    >
                        <option value="">All Tiers</option>
                        <option value="free">Free</option>
                        <option value="plus">Plus</option>
                        <option value="pro">Pro</option>
                        <option value="premium">Premium</option>
                    </select>
                </div>

                <div className="flex items-center gap-2">
                    <label className="text-sm font-handwritten text-pencil-black/60">Status:</label>
                    <select
                        value={statusFilter}
                        onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                        className="border-2 border-pencil-black/20 px-3 py-1.5 text-sm font-handwritten bg-white rounded-sm focus:border-ink-blue focus:outline-none"
                    >
                        <option value="">All Statuses</option>
                        <option value="active">Active</option>
                        <option value="suspended">Suspended</option>
                        <option value="banned">Banned</option>
                    </select>
                </div>
            </div>

            {/* ---- Error State ---- */}
            {error && (
                <div className="p-4 bg-marker-red/10 border-2 border-marker-red/30 flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-marker-red" />
                    <p className="font-handwritten text-marker-red">{error}</p>
                </div>
            )}

            {/* ---- User Table ---- */}
            {!error && (
                <SketchCard className="p-0 overflow-hidden hover:rotate-0">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b-2 border-pencil-black/10 bg-pencil-black/5">
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Email</th>
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Tier</th>
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Status</th>
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Apps</th>
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Joined</th>
                                    <th className="text-left px-4 py-3 text-sm font-marker uppercase tracking-wider text-pencil-black/60">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan={6} className="text-center py-12">
                                            <div className="animate-spin rounded-full h-8 w-8 border-4 border-dashed border-ink-blue mx-auto" />
                                        </td>
                                    </tr>
                                ) : data?.items.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="text-center py-12 font-handwritten text-pencil-black/40">
                                            No users found
                                        </td>
                                    </tr>
                                ) : (
                                    data?.items.map((user) => (
                                        <tr key={user.id} className="border-b border-pencil-black/5 hover:bg-pencil-black/[0.02] transition-colors">
                                            <td className="px-4 py-3">
                                                <span className="font-handwritten text-base">{user.email}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <TierBadge tier={user.tier} />
                                            </td>
                                            <td className="px-4 py-3">
                                                <UserStatusBadge status={user.status} />
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="font-marker text-lg">{user.application_count}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="text-sm font-handwritten text-pencil-black/50">
                                                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <select
                                                        value={user.tier}
                                                        onChange={(e) => handleTierChange(user.id, e.target.value)}
                                                        disabled={actionLoading === user.id}
                                                        className="text-xs border px-2 py-1 rounded-sm bg-white font-handwritten focus:outline-none focus:border-ink-blue"
                                                    >
                                                        <option value="free">Free</option>
                                                        <option value="plus">Plus</option>
                                                        <option value="pro">Pro</option>
                                                        <option value="premium">Premium</option>
                                                    </select>
                                                    <select
                                                        value={user.status}
                                                        onChange={(e) => handleStatusChange(user.id, e.target.value)}
                                                        disabled={actionLoading === user.id}
                                                        className="text-xs border px-2 py-1 rounded-sm bg-white font-handwritten focus:outline-none focus:border-ink-blue"
                                                    >
                                                        <option value="active">Active</option>
                                                        <option value="suspended">Suspend</option>
                                                        <option value="banned">Ban</option>
                                                    </select>
                                                    {actionLoading === user.id && (
                                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-dashed border-ink-blue" />
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* ---- Pagination ---- */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-between px-4 py-3 border-t-2 border-pencil-black/10 bg-pencil-black/[0.02]">
                            <span className="text-sm font-handwritten text-pencil-black/50">
                                Page {page} of {totalPages}
                            </span>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setPage(Math.max(1, page - 1))}
                                    disabled={page <= 1}
                                    className="p-1.5 border rounded-sm hover:bg-pencil-black/5 disabled:opacity-30 transition-colors"
                                >
                                    <ChevronLeft className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                                    disabled={page >= totalPages}
                                    className="p-1.5 border rounded-sm hover:bg-pencil-black/5 disabled:opacity-30 transition-colors"
                                >
                                    <ChevronRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    )}
                </SketchCard>
            )}
        </div>
    );
}
