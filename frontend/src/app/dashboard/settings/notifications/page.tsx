"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Bell, Mail, Smartphone, Clock, BellOff } from "lucide-react";
import Link from "next/link";

interface NotificationSetting {
  id: string;
  label: string;
  description: string;
  email: boolean;
  push: boolean;
}

export default function NotificationsPage() {
  const [settings, setSettings] = useState<NotificationSetting[]>([
    {
      id: "new_matches",
      label: "New Job Matches",
      description: "Get notified when AI finds jobs matching your persona",
      email: true,
      push: true,
    },
    {
      id: "application_status",
      label: "Application Updates",
      description: "Status changes on your submitted applications",
      email: true,
      push: true,
    },
    {
      id: "auto_apply",
      label: "Auto-Apply Results",
      description: "Notifications when auto-apply completes or fails",
      email: true,
      push: false,
    },
    {
      id: "weekly_digest",
      label: "Weekly Digest",
      description: "Summary of your job search activity",
      email: true,
      push: false,
    },
    {
      id: "tips",
      label: "Tips & Insights",
      description: "Career tips and job market insights",
      email: false,
      push: false,
    },
  ]);

  const [digestFrequency, setDigestFrequency] = useState("weekly");

  const toggleSetting = (id: string, type: "email" | "push") => {
    setSettings(settings.map(s =>
      s.id === id ? { ...s, [type]: !s[type] } : s
    ));
  };

  const handleSave = async () => {
    // TODO: API call
    alert("Notification preferences saved! (Mock)");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Notifications</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Control how we keep you in the loop.
        </p>
      </header>

      {/* Quick Toggle */}
      <SketchCard decoration="tape" className="p-6 bg-postit-yellow">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <BellOff className="w-8 h-8 text-pencil-black" />
            <div>
              <h2 className="text-2xl font-marker">Do Not Disturb</h2>
              <p className="font-handwritten text-pencil-black/70">Pause all notifications</p>
            </div>
          </div>
          <button className="px-6 py-3 border-2 border-pencil-black wobble bg-white font-handwritten text-lg hover:bg-pencil-black hover:text-white transition-all">
            Enable DND
          </button>
        </div>
      </SketchCard>

      {/* Notification Settings */}
      <div className="space-y-4">
        <div className="flex justify-end gap-8 px-4 font-marker text-lg">
          <span className="flex items-center gap-2"><Mail className="w-5 h-5" /> Email</span>
          <span className="flex items-center gap-2"><Smartphone className="w-5 h-5" /> Push</span>
        </div>

        {settings.map((setting) => (
          <SketchCard key={setting.id} decoration="none" className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1">
                <Bell className="w-6 h-6 text-ink-blue" />
                <div>
                  <h3 className="text-xl font-marker">{setting.label}</h3>
                  <p className="font-handwritten text-pencil-black/60">{setting.description}</p>
                </div>
              </div>
              <div className="flex gap-8">
                <button
                  onClick={() => toggleSetting(setting.id, "email")}
                  className={`w-12 h-12 border-2 border-pencil-black wobble flex items-center justify-center transition-all ${setting.email ? "bg-ink-blue text-white" : "bg-white"
                    }`}
                >
                  {setting.email ? "✓" : ""}
                </button>
                <button
                  onClick={() => toggleSetting(setting.id, "push")}
                  className={`w-12 h-12 border-2 border-pencil-black wobble flex items-center justify-center transition-all ${setting.push ? "bg-ink-blue text-white" : "bg-white"
                    }`}
                >
                  {setting.push ? "✓" : ""}
                </button>
              </div>
            </div>
          </SketchCard>
        ))}
      </div>

      {/* Digest Frequency */}
      <SketchCard decoration="none" className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-marker-red/10 rounded-full">
            <Clock className="w-6 h-6 text-marker-red" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-marker mb-4">Digest Frequency</h2>
            <div className="flex gap-4">
              {["daily", "weekly", "monthly", "never"].map((freq) => (
                <button
                  key={freq}
                  onClick={() => setDigestFrequency(freq)}
                  className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten text-lg capitalize transition-all ${digestFrequency === freq
                      ? "bg-marker-red text-white"
                      : "bg-white hover:bg-marker-red/10"
                    }`}
                >
                  {freq}
                </button>
              ))}
            </div>
          </div>
        </div>
      </SketchCard>

      <div className="flex justify-end">
        <SketchButton onClick={handleSave} variant="primary" className="text-xl px-8">
          Save Notifications
        </SketchButton>
      </div>
    </div>
  );
}
