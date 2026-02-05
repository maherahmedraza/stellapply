<<<<<<< HEAD
export default function Page() {
  return <div className="p-4">Placeholder Page</div>
=======
"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { Building2, MapPin, DollarSign, Clock, Bookmark, ExternalLink, Zap, Sparkles, ChevronLeft, Users, Globe, Briefcase } from "lucide-react";
import Link from "next/link";

// Mock job detail
const MOCK_JOB = {
  id: "1",
  title: "Senior Software Engineer",
  company: "Stripe",
  company_size: "10,000+ employees",
  company_industry: "Financial Technology",
  location: "San Francisco, CA",
  salary_range: "$180k - $250k",
  posted_date: "2 days ago",
  remote_type: "Hybrid",
  employment_type: "Full-time",
  match_score: 94,
  skills_match: 92,
  experience_match: 96,
  matching_skills: ["Python", "Go", "Distributed Systems", "PostgreSQL", "Redis", "AWS"],
  missing_skills: ["Ruby"],
  description: `Join Stripe's Core Infrastructure team to build the payment systems that power millions of businesses worldwide.

## About the Role
You'll work on distributed systems that handle millions of transactions per second, ensuring reliability, scalability, and performance at global scale.

## What You'll Do
- Design and implement core payment infrastructure
- Build high-performance APIs serving billions of requests
- Collaborate with cross-functional teams to launch new products
- Mentor junior engineers and contribute to engineering culture
- Participate in on-call rotation for critical systems

## What We're Looking For
- 5+ years of experience in backend development
- Strong experience with Python, Go, or similar languages
- Deep understanding of distributed systems
- Experience with databases (PostgreSQL, Redis, etc.)
- Track record of delivering complex projects`,
  requirements: [
    "5+ years backend development experience",
    "Strong Python or Go skills",
    "Distributed systems expertise",
    "Database experience (PostgreSQL, Redis)",
    "Bachelor's in CS or equivalent",
  ],
  benefits: [
    "Competitive salary and equity",
    "Comprehensive health insurance",
    "Flexible PTO",
    "Remote-friendly with office access",
    "Learning and development budget",
  ],
  apply_url: "https://stripe.com/jobs",
  source: "greenhouse",
  why_match: "Your 5+ years building payment systems at scale aligns perfectly with Stripe's infrastructure needs. Your Go and PostgreSQL experience are direct matches.",
};

export default function JobDetailPage() {
  const params = useParams();
  const [isSaved, setIsSaved] = useState(false);
  const job = MOCK_JOB; // In real app, fetch by params.id

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <header className="mb-6">
        <Link href="/dashboard/jobs" className="flex items-center gap-2 text-ink-blue hover:underline font-handwritten mb-4">
          <ChevronLeft className="w-4 h-4" /> Back to Search
        </Link>
      </header>

      {/* Main Card */}
      <SketchCard decoration="tape" className="p-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-4xl font-marker mb-2">{job.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-lg">
              <span className="flex items-center gap-2 font-handwritten">
                <Building2 className="w-5 h-5" /> {job.company}
              </span>
              <span className="flex items-center gap-2 font-handwritten text-pencil-black/60">
                <MapPin className="w-5 h-5" /> {job.location}
              </span>
            </div>
          </div>
          <div className="text-center bg-ink-blue/10 p-4 wobble">
            <div className="text-5xl font-marker text-ink-blue">{job.match_score}%</div>
            <span className="font-handwritten">Match</span>
          </div>
        </div>

        {/* Quick Info */}
        <div className="flex flex-wrap gap-3 mb-6">
          <span className="flex items-center gap-2 px-4 py-2 bg-postit-yellow wobble font-handwritten">
            <DollarSign className="w-5 h-5" /> {job.salary_range}
          </span>
          <span className={`px-4 py-2 wobble font-handwritten ${job.remote_type === "Remote" ? "bg-ink-blue text-white" : "bg-muted-paper"
            }`}>
            {job.remote_type}
          </span>
          <span className="flex items-center gap-2 px-4 py-2 bg-muted-paper wobble font-handwritten">
            <Briefcase className="w-5 h-5" /> {job.employment_type}
          </span>
          <span className="flex items-center gap-2 px-4 py-2 bg-muted-paper wobble font-handwritten">
            <Clock className="w-5 h-5" /> {job.posted_date}
          </span>
        </div>

        {/* AI Match Explanation */}
        <div className="bg-ink-blue text-white p-6 wobble mb-6">
          <div className="flex items-start gap-3">
            <Sparkles className="w-6 h-6 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-marker text-xl mb-2">Why You Match</h3>
              <p className="font-handwritten text-lg">{job.why_match}</p>
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="font-marker text-xl mb-3">Matching Skills ✓</h3>
            <div className="flex flex-wrap gap-2">
              {job.matching_skills.map((skill, i) => (
                <span key={i} className="px-3 py-1 bg-ink-blue/10 border-2 border-ink-blue wobble font-handwritten">
                  {skill}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h3 className="font-marker text-xl mb-3">Skills to Develop</h3>
            <div className="flex flex-wrap gap-2">
              {job.missing_skills.map((skill, i) => (
                <span key={i} className="px-3 py-1 bg-marker-red/10 border-2 border-marker-red/30 wobble font-handwritten">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <SketchButton variant="primary" className="flex-1 text-xl py-4 flex items-center justify-center gap-2">
            <Zap className="w-5 h-5" /> Apply with AI
          </SketchButton>
          <button
            onClick={() => setIsSaved(!isSaved)}
            className={`p-4 border-3 border-pencil-black wobble transition-all ${isSaved ? "bg-postit-yellow" : "bg-white hover:bg-postit-yellow"
              }`}
          >
            <Bookmark className={`w-6 h-6 ${isSaved ? "fill-current" : ""}`} />
          </button>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 border-3 border-pencil-black wobble bg-white hover:bg-muted-paper transition-all"
          >
            <ExternalLink className="w-6 h-6" />
          </a>
        </div>
      </SketchCard>

      {/* Company Info */}
      <SketchCard decoration="none" className="p-6">
        <h2 className="text-2xl font-marker mb-4">About {job.company}</h2>
        <div className="flex flex-wrap gap-6 text-lg font-handwritten">
          <span className="flex items-center gap-2">
            <Users className="w-5 h-5 text-ink-blue" /> {job.company_size}
          </span>
          <span className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-ink-blue" /> {job.company_industry}
          </span>
        </div>
      </SketchCard>

      {/* Job Description */}
      <SketchCard decoration="none" className="p-6">
        <h2 className="text-2xl font-marker mb-4">Job Description</h2>
        <div className="prose prose-lg max-w-none font-handwritten whitespace-pre-line">
          {job.description}
        </div>
      </SketchCard>

      {/* Requirements */}
      <SketchCard decoration="none" className="p-6">
        <h2 className="text-2xl font-marker mb-4">Requirements</h2>
        <ul className="space-y-2">
          {job.requirements.map((req, i) => (
            <li key={i} className="flex items-start gap-3 font-handwritten text-lg">
              <span className="text-ink-blue">•</span> {req}
            </li>
          ))}
        </ul>
      </SketchCard>

      {/* Benefits */}
      <SketchCard decoration="none" className="p-6 bg-postit-yellow/30">
        <h2 className="text-2xl font-marker mb-4">Benefits</h2>
        <ul className="space-y-2">
          {job.benefits.map((benefit, i) => (
            <li key={i} className="flex items-start gap-3 font-handwritten text-lg">
              <span className="text-ink-blue">✓</span> {benefit}
            </li>
          ))}
        </ul>
      </SketchCard>

      {/* Bottom CTA */}
      <div className="sticky bottom-4 bg-paper-bg p-4 wobble border-3 border-pencil-black shadow-sketch-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-marker text-xl">{job.title} at {job.company}</p>
            <p className="font-handwritten text-pencil-black/60">{job.match_score}% match • {job.salary_range}</p>
          </div>
          <SketchButton variant="primary" className="flex items-center gap-2">
            <Zap className="w-4 h-4" /> Apply Now
          </SketchButton>
        </div>
      </div>
    </div>
  );
>>>>>>> feature/resume-upload-gdpr-compliance
}
