"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Zap, Building2, MapPin, DollarSign, Clock, Bookmark, ExternalLink, Sparkles, RefreshCw } from "lucide-react";
import Link from "next/link";

interface MatchedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  posted_date: string;
  remote_type: string;
  match_score: number;
  skills_match: number;
  experience_match: number;
  matching_skills: string[];
  missing_skills: string[];
  why_match: string;
}

// Mock matched jobs
const MOCK_MATCHES: MatchedJob[] = [
  {
    id: "1",
    title: "Senior Software Engineer",
    company: "Stripe",
    location: "San Francisco, CA",
    salary_range: "$180k - $250k",
    posted_date: "2 days ago",
    remote_type: "Hybrid",
    match_score: 94,
    skills_match: 92,
    experience_match: 96,
    matching_skills: ["Python", "Go", "Distributed Systems", "PostgreSQL", "Redis"],
    missing_skills: ["Ruby"],
    why_match: "Your 5+ years building payment systems at scale aligns perfectly with Stripe's infrastructure needs.",
  },
  {
    id: "2",
    title: "Staff Data Engineer",
    company: "Airbnb",
    location: "Remote",
    salary_range: "$200k - $280k",
    posted_date: "1 day ago",
    remote_type: "Remote",
    match_score: 91,
    skills_match: 95,
    experience_match: 88,
    matching_skills: ["Spark", "Airflow", "Python", "SQL", "Kafka"],
    missing_skills: ["Flink"],
    why_match: "Your data pipeline experience matches their modern data stack. Remote preference is a perfect fit.",
  },
  {
    id: "3",
    title: "Backend Engineer",
    company: "OpenAI",
    location: "San Francisco, CA",
    salary_range: "$220k - $350k",
    posted_date: "3 days ago",
    remote_type: "Onsite",
    match_score: 88,
    skills_match: 85,
    experience_match: 90,
    matching_skills: ["Python", "ML Infrastructure", "Distributed Systems"],
    missing_skills: ["CUDA", "PyTorch"],
    why_match: "Your infrastructure background is valuable for scaling LLM training and serving.",
  },
];

function MatchCard({ job }: { job: MatchedJob }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <SketchCard
      decoration="none"
      className={`p-6 transition-all hover-lift ${job.match_score >= 90 ? "border-l-4 border-l-ink-blue" : ""
        }`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <Link href={`/dashboard/jobs/${job.id}`}>
            <h3 className="text-2xl font-marker hover:text-ink-blue transition-colors">{job.title}</h3>
          </Link>
          <div className="flex items-center gap-4 mt-1">
            <span className="flex items-center gap-1 font-handwritten text-lg">
              <Building2 className="w-4 h-4" /> {job.company}
            </span>
            <span className="flex items-center gap-1 font-handwritten text-pencil-black/60">
              <MapPin className="w-4 h-4" /> {job.location}
            </span>
          </div>
        </div>
        <div className="text-center">
          <div className={`text-4xl font-marker ${job.match_score >= 90 ? "text-ink-blue" : "text-pencil-black"
            }`}>
            {job.match_score}%
          </div>
          <span className="text-sm font-handwritten text-pencil-black/60">Match</span>
        </div>
      </div>

      {/* AI Explanation */}
      <div className="bg-ink-blue/5 wobble p-4 mb-4">
        <div className="flex items-start gap-2">
          <Sparkles className="w-5 h-5 text-ink-blue flex-shrink-0 mt-1" />
          <p className="font-handwritten">{job.why_match}</p>
        </div>
      </div>

      {/* Skills Breakdown */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-ink-blue font-handwritten hover:underline mb-4"
      >
        {expanded ? "Hide details ↑" : "Show match details ↓"}
      </button>

      {expanded && (
        <div className="space-y-4 mb-4 animate-in fade-in">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="font-marker text-sm mb-2">Skills Match: {job.skills_match}%</p>
              <div className="h-2 bg-muted-paper rounded">
                <div
                  className="h-full bg-ink-blue rounded"
                  style={{ width: `${job.skills_match}%` }}
                />
              </div>
            </div>
            <div>
              <p className="font-marker text-sm mb-2">Experience Match: {job.experience_match}%</p>
              <div className="h-2 bg-muted-paper rounded">
                <div
                  className="h-full bg-ink-blue rounded"
                  style={{ width: `${job.experience_match}%` }}
                />
              </div>
            </div>
          </div>

          <div>
            <p className="font-marker text-sm mb-2">Matching Skills</p>
            <div className="flex flex-wrap gap-2">
              {job.matching_skills.map((skill, i) => (
                <span key={i} className="px-2 py-1 bg-ink-blue/10 border border-ink-blue wobble text-sm font-handwritten">
                  ✓ {skill}
                </span>
              ))}
            </div>
          </div>

          {job.missing_skills.length > 0 && (
            <div>
              <p className="font-marker text-sm mb-2">Skills to Learn</p>
              <div className="flex flex-wrap gap-2">
                {job.missing_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-1 bg-marker-red/10 border border-marker-red/30 wobble text-sm font-handwritten">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-wrap gap-3 mb-4">
        {job.salary_range && (
          <span className="flex items-center gap-1 px-3 py-1 bg-postit-yellow wobble font-handwritten text-sm">
            <DollarSign className="w-4 h-4" /> {job.salary_range}
          </span>
        )}
        <span className="flex items-center gap-1 px-3 py-1 bg-muted-paper wobble font-handwritten text-sm">
          <Clock className="w-4 h-4" /> {job.posted_date}
        </span>
        <span className={`px-3 py-1 wobble font-handwritten text-sm ${job.remote_type === "Remote" ? "bg-ink-blue text-white" : "bg-muted-paper"
          }`}>
          {job.remote_type}
        </span>
      </div>

      <div className="flex gap-3">
        <SketchButton variant="primary" className="flex-1 flex items-center justify-center gap-2">
          <Zap className="w-4 h-4" /> Apply with AI
        </SketchButton>
        <button className="p-3 border-2 border-pencil-black wobble bg-white hover:bg-postit-yellow transition-all">
          <Bookmark className="w-5 h-5" />
        </button>
        <a href="#" className="p-3 border-2 border-pencil-black wobble bg-white hover:bg-muted-paper transition-all">
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
    </SketchCard>
  );
}

export default function JobMatchesPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/jobs" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Job Search
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">AI Matches</h1>
            <p className="text-xl font-handwritten text-pencil-black/70">
              Jobs handpicked by AI based on your skills and preferences.
            </p>
          </div>
          <SketchButton
            variant="secondary"
            onClick={handleRefresh}
            className="flex items-center gap-2"
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
            {isRefreshing ? "Matching..." : "Refresh"}
          </SketchButton>
        </div>
      </header>

      {/* Stats */}
      <SketchCard decoration="tape" className="p-6 bg-ink-blue/5">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-4xl font-marker text-ink-blue">{MOCK_MATCHES.length}</p>
            <p className="font-handwritten text-pencil-black/60">New Matches</p>
          </div>
          <div>
            <p className="text-4xl font-marker text-pencil-black">91%</p>
            <p className="font-handwritten text-pencil-black/60">Avg Match</p>
          </div>
          <div>
            <p className="text-4xl font-marker text-marker-red">3</p>
            <p className="font-handwritten text-pencil-black/60">90%+ Matches</p>
          </div>
        </div>
      </SketchCard>

      {/* Match List */}
      <div className="space-y-6">
        {MOCK_MATCHES.map(job => (
          <MatchCard key={job.id} job={job} />
        ))}
      </div>

      {MOCK_MATCHES.length === 0 && (
        <SketchCard decoration="none" className="p-12 text-center">
          <Sparkles className="w-16 h-16 mx-auto text-pencil-black/20 mb-4" />
          <h3 className="text-2xl font-marker mb-2">No matches yet</h3>
          <p className="font-handwritten text-pencil-black/60 mb-4">
            Complete your persona to get AI-powered job matches
          </p>
          <Link href="/dashboard/persona">
            <SketchButton variant="primary">Build Your Persona</SketchButton>
          </Link>
        </SketchCard>
      )}
    </div>
  );
}
