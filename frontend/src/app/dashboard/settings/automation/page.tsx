"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Zap, Play, Pause, Clock, BarChart3, AlertTriangle } from "lucide-react";
import Link from "next/link";

export default function AutomationPage() {
  const [autoApplyEnabled, setAutoApplyEnabled] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [dailyLimit, setDailyLimit] = useState(5);

  // Mock stats
  const stats = {
    appliedToday: 3,
    appliedThisWeek: 12,
    successRate: 78,
    queuedJobs: 7,
  };

  const handleToggle = () => {
    setAutoApplyEnabled(!autoApplyEnabled);
  };

  const handlePause = () => {
    setIsPaused(!isPaused);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Automation Settings</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Configure your AI-powered auto-apply engine.
        </p>
      </header>

      {/* Main Toggle */}
      <SketchCard decoration="tape" className={`p-6 ${autoApplyEnabled ? "bg-ink-blue/10" : "bg-muted-paper"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`p-4 rounded-full ${autoApplyEnabled ? "bg-ink-blue" : "bg-pencil-black/20"}`}>
              <Zap className={`w-8 h-8 ${autoApplyEnabled ? "text-white" : "text-pencil-black/40"}`} />
            </div>
            <div>
              <h2 className="text-3xl font-marker">Auto-Apply Engine</h2>
              <p className="font-handwritten text-xl text-pencil-black/70">
                {autoApplyEnabled ? "Active and applying to jobs" : "Currently disabled"}
              </p>
            </div>
          </div>
          <button
            onClick={handleToggle}
            className={`px-8 py-4 border-3 border-pencil-black wobble font-marker text-2xl transition-all ${autoApplyEnabled
                ? "bg-ink-blue text-white hover:bg-ink-blue/80"
                : "bg-white hover:bg-ink-blue hover:text-white"
              }`}
          >
            {autoApplyEnabled ? "Enabled" : "Disabled"}
          </button>
        </div>
      </SketchCard>

      {/* Pause Controls */}
      {autoApplyEnabled && (
        <SketchCard decoration="none" className="p-6 bg-postit-yellow">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {isPaused ? (
                <Play className="w-8 h-8 text-pencil-black" />
              ) : (
                <Pause className="w-8 h-8 text-pencil-black" />
              )}
              <div>
                <h3 className="text-2xl font-marker">
                  {isPaused ? "Queue Paused" : "Queue Active"}
                </h3>
                <p className="font-handwritten text-pencil-black/70">
                  {isPaused
                    ? "No applications will be sent until resumed"
                    : `${stats.queuedJobs} jobs waiting in queue`}
                </p>
              </div>
            </div>
            <SketchButton onClick={handlePause} variant={isPaused ? "primary" : "secondary"}>
              {isPaused ? "Resume Queue" : "Pause Queue"}
            </SketchButton>
          </div>
        </SketchCard>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-4xl font-marker text-ink-blue">{stats.appliedToday}</p>
          <p className="font-handwritten text-pencil-black/60">Today</p>
        </SketchCard>
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-4xl font-marker text-marker-red">{stats.appliedThisWeek}</p>
          <p className="font-handwritten text-pencil-black/60">This Week</p>
        </SketchCard>
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-4xl font-marker text-ink-blue">{stats.successRate}%</p>
          <p className="font-handwritten text-pencil-black/60">Success Rate</p>
        </SketchCard>
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-4xl font-marker text-pencil-black">{stats.queuedJobs}</p>
          <p className="font-handwritten text-pencil-black/60">In Queue</p>
        </SketchCard>
      </div>

      {/* Limits */}
      <SketchCard decoration="none" className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-marker-red/10 rounded-full">
            <Clock className="w-6 h-6 text-marker-red" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-marker mb-4">Daily Application Limit</h2>
            <p className="font-handwritten text-pencil-black/60 mb-4">
              Maximum applications to send per day. Your plan allows up to 8/day.
            </p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="8"
                value={dailyLimit}
                onChange={(e) => setDailyLimit(parseInt(e.target.value))}
                className="flex-1 h-3 bg-muted-paper rounded-full appearance-none cursor-pointer"
              />
              <span className="text-3xl font-marker w-16 text-center">{dailyLimit}</span>
            </div>
          </div>
        </div>
      </SketchCard>

      {/* Safety Notice */}
      <SketchCard decoration="none" className="p-6 border-marker-red border-[3px]">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-8 h-8 text-marker-red flex-shrink-0" />
          <div>
            <h3 className="text-xl font-marker text-marker-red mb-2">Human-Like Behavior</h3>
            <p className="font-handwritten text-pencil-black/70">
              Our automation uses randomized timing, human-like typing patterns, and smart scheduling
              to apply during business hours in the employer&apos;s timezone. This keeps your applications
              looking authentic and avoids detection.
            </p>
          </div>
        </div>
      </SketchCard>

      <div className="flex justify-end">
        <SketchButton variant="primary" className="text-xl px-8">
          Save Automation Settings
        </SketchButton>
      </div>
    </div>
  );
}
