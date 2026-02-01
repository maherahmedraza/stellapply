"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Bookmark, Building2, MapPin, DollarSign, Clock, Trash2, Zap, ExternalLink, FolderOpen } from "lucide-react";
import Link from "next/link";

interface SavedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  saved_date: string;
  remote_type: string;
  match_score: number;
  notes?: string;
}

// Mock saved jobs
const MOCK_SAVED: SavedJob[] = [
  {
    id: "1",
    title: "Senior Software Engineer",
    company: "Stripe",
    location: "San Francisco, CA",
    salary_range: "$180k - $250k",
    saved_date: "Today",
    remote_type: "Hybrid",
    match_score: 94,
    notes: "Perfect match! Applied to similar role last month.",
  },
  {
    id: "4",
    title: "Platform Engineer",
    company: "Figma",
    location: "Remote (US)",
    salary_range: "$170k - $230k",
    saved_date: "Yesterday",
    remote_type: "Remote",
    match_score: 85,
  },
  {
    id: "5",
    title: "Senior ML Engineer",
    company: "Notion",
    location: "New York, NY",
    salary_range: "$190k - $270k",
    saved_date: "3 days ago",
    remote_type: "Hybrid",
    match_score: 82,
    notes: "Interesting ML focus. Need to brush up on NLP.",
  },
];

export default function SavedJobsPage() {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>(MOCK_SAVED);
  const [editingNote, setEditingNote] = useState<string | null>(null);

  const removeJob = (jobId: string) => {
    setSavedJobs(prev => prev.filter(j => j.id !== jobId));
  };

  const updateNote = (jobId: string, note: string) => {
    setSavedJobs(prev => prev.map(j =>
      j.id === jobId ? { ...j, notes: note } : j
    ));
    setEditingNote(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/jobs" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Job Search
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Saved Jobs</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Jobs you&apos;ve bookmarked for later. {savedJobs.length} saved.
        </p>
      </header>

      {savedJobs.length > 0 ? (
        <div className="space-y-4">
          {savedJobs.map(job => (
            <SketchCard key={job.id} decoration="none" className="p-6 group">
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <Link href={`/dashboard/jobs/${job.id}`}>
                    <h3 className="text-2xl font-marker hover:text-ink-blue transition-colors">
                      {job.title}
                    </h3>
                  </Link>
                  <div className="flex items-center gap-4 mt-1">
                    <span className="flex items-center gap-1 font-handwritten">
                      <Building2 className="w-4 h-4" /> {job.company}
                    </span>
                    <span className="flex items-center gap-1 font-handwritten text-pencil-black/60">
                      <MapPin className="w-4 h-4" /> {job.location}
                    </span>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-marker text-ink-blue">{job.match_score}%</div>
                  <span className="text-xs font-handwritten text-pencil-black/60">match</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-3 mb-4">
                {job.salary_range && (
                  <span className="flex items-center gap-1 px-3 py-1 bg-postit-yellow wobble font-handwritten text-sm">
                    <DollarSign className="w-4 h-4" /> {job.salary_range}
                  </span>
                )}
                <span className={`px-3 py-1 wobble font-handwritten text-sm ${job.remote_type === "Remote" ? "bg-ink-blue text-white" : "bg-muted-paper"
                  }`}>
                  {job.remote_type}
                </span>
                <span className="flex items-center gap-1 px-3 py-1 bg-muted-paper wobble font-handwritten text-sm">
                  <Bookmark className="w-4 h-4" /> Saved {job.saved_date}
                </span>
              </div>

              {/* Notes */}
              <div className="mb-4">
                {editingNote === job.id ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      defaultValue={job.notes || ""}
                      placeholder="Add a note..."
                      className="flex-1 p-2 border-2 border-pencil-black wobble bg-white font-handwritten"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          updateNote(job.id, e.currentTarget.value);
                        }
                      }}
                      autoFocus
                    />
                    <button
                      onClick={() => setEditingNote(null)}
                      className="px-3 py-1 border-2 border-pencil-black wobble bg-muted-paper"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setEditingNote(job.id)}
                    className="text-pencil-black/60 font-handwritten hover:text-ink-blue transition-colors"
                  >
                    {job.notes || "+ Add note"}
                  </button>
                )}
              </div>

              <div className="flex gap-3">
                <SketchButton variant="primary" className="flex-1 flex items-center justify-center gap-2">
                  <Zap className="w-4 h-4" /> Apply Now
                </SketchButton>
                <a href="#" className="p-3 border-2 border-pencil-black wobble bg-white hover:bg-muted-paper transition-all">
                  <ExternalLink className="w-5 h-5" />
                </a>
                <button
                  onClick={() => removeJob(job.id)}
                  className="p-3 border-2 border-pencil-black wobble bg-white hover:bg-marker-red hover:text-white transition-all"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </SketchCard>
          ))}
        </div>
      ) : (
        <SketchCard decoration="none" className="p-12 text-center">
          <FolderOpen className="w-16 h-16 mx-auto text-pencil-black/20 mb-4" />
          <h3 className="text-2xl font-marker mb-2">No saved jobs yet</h3>
          <p className="font-handwritten text-pencil-black/60 mb-4">
            Browse jobs and click the bookmark icon to save them here.
          </p>
          <Link href="/dashboard/jobs">
            <SketchButton variant="primary">Browse Jobs</SketchButton>
          </Link>
        </SketchCard>
      )}
    </div>
  );
}
