"use client";

import React, { useState } from "react";
import { SketchCard, SketchButton, SketchInput } from "@/components/ui/hand-drawn";
import { Search, MapPin, Building2, DollarSign, Clock, Bookmark, ExternalLink, Zap, Filter, X, Trophy, TrendingUp } from "lucide-react";
import Link from "next/link";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  posted_date: string;
  remote_type: string;
  match_score?: number;
  description: string;
  source: string;
  // LinkedIn-style matching
  skills_match_count?: number;
  total_required_skills?: number;
  matching_skills?: string[];
  is_top_applicant?: boolean;
}

// Mock jobs for demo
const MOCK_JOBS: Job[] = [
  {
    id: "1",
    title: "Senior Software Engineer",
    company: "Stripe",
    location: "San Francisco, CA",
    salary_range: "$180k - $250k",
    posted_date: "2 days ago",
    remote_type: "Hybrid",
    match_score: 94,
    description: "Build payment infrastructure that powers millions of businesses. Work with Go, Ruby, and distributed systems at scale.",
    source: "greenhouse",
    skills_match_count: 6,
    total_required_skills: 7,
    matching_skills: ["Python", "Go", "PostgreSQL", "Redis", "AWS", "Distributed Systems"],
    is_top_applicant: true,
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
    description: "Design and build data pipelines using Spark, Airflow, and modern data stack. Lead projects that impact millions of hosts and guests.",
    source: "lever",
    skills_match_count: 5,
    total_required_skills: 6,
    matching_skills: ["Spark", "Airflow", "Python", "SQL", "Kafka"],
    is_top_applicant: true,
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
    description: "Build infrastructure for training and serving large language models. Python, distributed systems, and ML experience preferred.",
    source: "greenhouse",
    skills_match_count: 4,
    total_required_skills: 6,
    matching_skills: ["Python", "ML Infrastructure", "Distributed Systems", "AWS"],
    is_top_applicant: false,
  },
  {
    id: "4",
    title: "Platform Engineer",
    company: "Figma",
    location: "Remote (US)",
    salary_range: "$170k - $230k",
    posted_date: "5 days ago",
    remote_type: "Remote",
    match_score: 85,
    description: "Build and scale the platform that powers Figma. Work on CI/CD, Kubernetes, and developer tooling.",
    source: "greenhouse",
    skills_match_count: 4,
    total_required_skills: 5,
    matching_skills: ["Kubernetes", "Docker", "AWS", "Go"],
    is_top_applicant: false,
  },
  {
    id: "5",
    title: "Senior ML Engineer",
    company: "Notion",
    location: "New York, NY",
    salary_range: "$190k - $270k",
    posted_date: "1 week ago",
    remote_type: "Hybrid",
    match_score: 82,
    description: "Build ML features that help teams organize their knowledge. Experience with NLP and recommendation systems.",
    source: "lever",
    skills_match_count: 3,
    total_required_skills: 5,
    matching_skills: ["Python", "SQL", "ML"],
    is_top_applicant: false,
  },
];

function JobCard({ job, isSaved, onSave }: { job: Job; isSaved: boolean; onSave: () => void }) {
  const matchColor = job.match_score
    ? job.match_score >= 90 ? "text-ink-blue"
      : job.match_score >= 80 ? "text-pencil-black"
        : "text-pencil-black/60"
    : "text-pencil-black/40";

  const skillsPercentage = job.skills_match_count && job.total_required_skills
    ? Math.round((job.skills_match_count / job.total_required_skills) * 100)
    : 0;

  return (
    <SketchCard decoration="none" className={`p-6 hover-lift transition-all cursor-pointer group ${job.is_top_applicant ? "border-l-4 border-l-ink-blue" : ""}`}>
      {/* Top Applicant Badge */}
      {job.is_top_applicant && (
        <div className="flex items-center gap-2 mb-3 -mt-2">
          <span className="flex items-center gap-1 px-2 py-1 bg-ink-blue text-white text-xs font-marker wobble">
            <Trophy className="w-3 h-3" /> TOP APPLICANT
          </span>
          <span className="font-handwritten text-xs text-pencil-black/60">You&apos;re in the top 10% of applicants</span>
        </div>
      )}

      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <Link href={`/dashboard/jobs/${job.id}`}>
            <h3 className="text-2xl font-marker group-hover:text-ink-blue transition-colors">{job.title}</h3>
          </Link>
          <div className="flex items-center gap-2 mt-1">
            <Building2 className="w-4 h-4 text-pencil-black/60" />
            <span className="font-handwritten text-lg">{job.company}</span>
          </div>
        </div>
        {job.match_score && (
          <div className={`text-3xl font-marker ${matchColor}`}>
            {job.match_score}%
            <span className="text-sm block text-center">match</span>
          </div>
        )}
      </div>

      {/* Skills Match Bar - LinkedIn style */}
      {job.skills_match_count !== undefined && job.total_required_skills && (
        <div className="mb-4 p-3 bg-muted-paper/50 wobble">
          <div className="flex justify-between items-center mb-2">
            <span className="flex items-center gap-2 font-handwritten text-sm">
              <TrendingUp className="w-4 h-4 text-ink-blue" />
              Skills Match
            </span>
            <span className="font-marker text-sm">
              {job.skills_match_count} of {job.total_required_skills} skills
            </span>
          </div>
          <div className="h-2 bg-pencil-black/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-ink-blue rounded-full transition-all"
              style={{ width: `${skillsPercentage}%` }}
            />
          </div>
          {job.matching_skills && job.matching_skills.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {job.matching_skills.slice(0, 4).map((skill, i) => (
                <span key={i} className="px-2 py-0.5 bg-ink-blue/10 text-xs font-handwritten border border-ink-blue/20">
                  ✓ {skill}
                </span>
              ))}
              {job.matching_skills.length > 4 && (
                <span className="px-2 py-0.5 text-xs font-handwritten text-pencil-black/60">
                  +{job.matching_skills.length - 4} more
                </span>
              )}
            </div>
          )}
        </div>
      )}

      <p className="font-handwritten text-pencil-black/70 mb-4 line-clamp-2">{job.description}</p>

      <div className="flex flex-wrap gap-3 mb-4">
        <span className="flex items-center gap-1 px-3 py-1 bg-muted-paper wobble font-handwritten text-sm">
          <MapPin className="w-4 h-4" /> {job.location}
        </span>
        {job.salary_range && (
          <span className="flex items-center gap-1 px-3 py-1 bg-postit-yellow wobble font-handwritten text-sm">
            <DollarSign className="w-4 h-4" /> {job.salary_range}
          </span>
        )}
        <span className="flex items-center gap-1 px-3 py-1 bg-ink-blue/10 wobble font-handwritten text-sm">
          <Clock className="w-4 h-4" /> {job.posted_date}
        </span>
        <span className={`px-3 py-1 wobble font-handwritten text-sm ${job.remote_type === "Remote" ? "bg-ink-blue text-white" : "bg-muted-paper"
          }`}>
          {job.remote_type}
        </span>
      </div>

      <div className="flex gap-3">
        <SketchButton variant="primary" className="flex-1 flex items-center justify-center gap-2">
          <Zap className="w-4 h-4" /> Quick Apply
        </SketchButton>
        <button
          onClick={(e) => { e.preventDefault(); onSave(); }}
          className={`p-3 border-2 border-pencil-black wobble transition-all ${isSaved ? "bg-postit-yellow" : "bg-white hover:bg-postit-yellow"
            }`}
        >
          <Bookmark className={`w-5 h-5 ${isSaved ? "fill-current" : ""}`} />
        </button>
        <a
          href="#"
          className="p-3 border-2 border-pencil-black wobble bg-white hover:bg-muted-paper transition-all"
          onClick={(e) => e.preventDefault()}
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
    </SketchCard>
  );
}

export default function JobSearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [location, setLocation] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [savedJobs, setSavedJobs] = useState<string[]>([]);
  const [jobs] = useState<Job[]>(MOCK_JOBS);

  const handleSearch = () => {
    // TODO: API call
    console.log("Searching:", { searchQuery, location, remoteOnly });
  };

  const toggleSave = (jobId: string) => {
    setSavedJobs(prev =>
      prev.includes(jobId)
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    );
  };

  const filteredJobs = jobs.filter(job => {
    if (searchQuery && !job.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    if (location && !job.location.toLowerCase().includes(location.toLowerCase())) return false;
    if (remoteOnly && job.remote_type !== "Remote") return false;
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Job Search</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          AI-powered matching finds the best opportunities for you.
        </p>
      </header>

      {/* Search Bar */}
      <SketchCard decoration="tape" className="p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
            <input
              type="text"
              placeholder="Job title, keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-pencil-black wobble bg-white dark:bg-muted-paper font-handwritten text-lg"
            />
          </div>
          <div className="flex-1 relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
            <input
              type="text"
              placeholder="Location or Remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-pencil-black wobble bg-white dark:bg-muted-paper font-handwritten text-lg"
            />
          </div>
          <SketchButton onClick={handleSearch} variant="primary" className="text-lg px-8">
            Search
          </SketchButton>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-3 border-2 border-pencil-black wobble transition-all ${showFilters ? "bg-ink-blue text-white" : "bg-white"
              }`}
          >
            <Filter className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t-2 border-dashed border-pencil-black/20 flex flex-wrap gap-4">
            <label className="flex items-center gap-2 font-handwritten cursor-pointer">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={(e) => setRemoteOnly(e.target.checked)}
                className="w-5 h-5"
              />
              Remote Only
            </label>
            {/* More filters can be added */}
          </div>
        )}
      </SketchCard>

      {/* Quick Links */}
      <div className="flex gap-4">
        <Link href="/dashboard/jobs/matches">
          <SketchButton variant="secondary" className="flex items-center gap-2">
            <Zap className="w-4 h-4" /> AI Matches ({MOCK_JOBS.length})
          </SketchButton>
        </Link>
        <Link href="/dashboard/jobs/saved">
          <SketchButton variant="secondary" className="flex items-center gap-2">
            <Bookmark className="w-4 h-4" /> Saved ({savedJobs.length})
          </SketchButton>
        </Link>
      </div>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-marker">{filteredJobs.length} Jobs Found</h2>
          <select className="px-4 py-2 border-2 border-pencil-black wobble bg-white font-handwritten">
            <option>Best Match</option>
            <option>Most Recent</option>
            <option>Highest Salary</option>
          </select>
        </div>

        {filteredJobs.map(job => (
          <JobCard
            key={job.id}
            job={job}
            isSaved={savedJobs.includes(job.id)}
            onSave={() => toggleSave(job.id)}
          />
        ))}

        {filteredJobs.length === 0 && (
          <SketchCard decoration="none" className="p-12 text-center">
            <Search className="w-16 h-16 mx-auto text-pencil-black/20 mb-4" />
            <h3 className="text-2xl font-marker mb-2">No jobs found</h3>
            <p className="font-handwritten text-pencil-black/60">
              Try adjusting your search criteria
            </p>
          </SketchCard>
        )}
      </div>
    </div>
  );
}
