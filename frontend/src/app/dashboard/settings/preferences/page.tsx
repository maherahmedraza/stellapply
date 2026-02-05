"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { MapPin, Briefcase, DollarSign, Building2, Globe } from "lucide-react";
import Link from "next/link";

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState({
    targetRoles: ["Software Engineer", "Data Engineer"],
    locations: ["Remote", "San Francisco", "New York"],
    salaryMin: 120000,
    salaryMax: 180000,
    remotePreference: "remote",
    industries: ["Technology", "Finance", "Healthcare"],
    companySize: ["startup", "medium"],
  });

  const handleSave = async () => {
    // TODO: API call to save preferences
    alert("Preferences saved! (Mock)");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Job Preferences</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Sketch out your ideal job search parameters.
        </p>
      </header>

      <div className="grid gap-6">
        {/* Target Roles */}
        <SketchCard decoration="tape" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-ink-blue/10 rounded-full">
              <Briefcase className="w-6 h-6 text-ink-blue" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Target Roles</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {preferences.targetRoles.map((role, i) => (
                  <span key={i} className="px-3 py-1 bg-ink-blue/10 border-2 border-ink-blue wobble font-handwritten">
                    {role}
                  </span>
                ))}
              </div>
              <input
                type="text"
                placeholder="Add a role..."
                className="w-full p-3 border-2 border-pencil-black wobble bg-white dark:bg-muted-paper font-handwritten"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && e.currentTarget.value) {
                    setPreferences({
                      ...preferences,
                      targetRoles: [...preferences.targetRoles, e.currentTarget.value]
                    });
                    e.currentTarget.value = "";
                  }
                }}
              />
            </div>
          </div>
        </SketchCard>

        {/* Locations */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-marker-red/10 rounded-full">
              <MapPin className="w-6 h-6 text-marker-red" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Preferred Locations</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {preferences.locations.map((loc, i) => (
                  <span key={i} className="px-3 py-1 bg-marker-red/10 border-2 border-marker-red wobble font-handwritten">
                    {loc}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Salary Range */}
        <SketchCard decoration="none" className="p-6 bg-postit-yellow">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-pencil-black/10 rounded-full">
              <DollarSign className="w-6 h-6 text-pencil-black" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Salary Range</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="font-handwritten text-lg block mb-2">Minimum</label>
                  <input
                    type="number"
                    value={preferences.salaryMin}
                    onChange={(e) => setPreferences({ ...preferences, salaryMin: parseInt(e.target.value) })}
                    className="w-full p-3 border-2 border-pencil-black wobble bg-white font-handwritten text-xl"
                  />
                </div>
                <div>
                  <label className="font-handwritten text-lg block mb-2">Maximum</label>
                  <input
                    type="number"
                    value={preferences.salaryMax}
                    onChange={(e) => setPreferences({ ...preferences, salaryMax: parseInt(e.target.value) })}
                    className="w-full p-3 border-2 border-pencil-black wobble bg-white font-handwritten text-xl"
                  />
                </div>
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Remote Preference */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-ink-blue/10 rounded-full">
              <Globe className="w-6 h-6 text-ink-blue" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Work Setting</h2>
              <div className="flex gap-4">
                {["remote", "hybrid", "onsite", "any"].map((option) => (
                  <button
                    key={option}
                    onClick={() => setPreferences({ ...preferences, remotePreference: option })}
                    className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten text-lg capitalize transition-all ${preferences.remotePreference === option
                        ? "bg-ink-blue text-white"
                        : "bg-white hover:bg-ink-blue/10"
                      }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Company Size */}
        <SketchCard decoration="none" className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-postit-yellow rounded-full">
              <Building2 className="w-6 h-6 text-pencil-black" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-marker mb-4">Company Size</h2>
              <div className="flex flex-wrap gap-3">
                {[
                  { id: "startup", label: "Startup (1-50)" },
                  { id: "small", label: "Small (51-200)" },
                  { id: "medium", label: "Medium (201-1000)" },
                  { id: "large", label: "Large (1000+)" },
                  { id: "enterprise", label: "Enterprise (10000+)" },
                ].map((size) => (
                  <button
                    key={size.id}
                    onClick={() => {
                      const current = preferences.companySize;
                      const updated = current.includes(size.id)
                        ? current.filter(s => s !== size.id)
                        : [...current, size.id];
                      setPreferences({ ...preferences, companySize: updated });
                    }}
                    className={`px-4 py-2 border-2 border-pencil-black wobble font-handwritten transition-all ${preferences.companySize.includes(size.id)
                        ? "bg-pencil-black text-white"
                        : "bg-white hover:bg-muted-paper"
                      }`}
                  >
                    {size.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </SketchCard>
      </div>

      <div className="flex justify-end">
        <SketchButton onClick={handleSave} variant="primary" className="text-xl px-8">
          Save Preferences
        </SketchButton>
      </div>
    </div>
  );
}
