'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { SketchButton, SketchInput } from "@/components/ui/hand-drawn"

// Mock job data
const mockJobs = [
  {
    id: '1',
    title: 'Senior Software Engineer',
    company: 'TechCorp Inc.',
    location: 'Berlin, Germany',
    salary: '€80,000 - €120,000',
    matchScore: 92,
    postedAt: '2 days ago'
  },
  {
    id: '2',
    title: 'Full Stack Developer',
    company: 'StartupHub',
    location: 'Munich, Germany',
    salary: '€70,000 - €95,000',
    matchScore: 85,
    postedAt: '1 week ago'
  },
  {
    id: '3',
    title: 'Backend Developer (Python)',
    company: 'DataFlow GmbH',
    location: 'Remote',
    salary: '€75,000 - €100,000',
    matchScore: 88,
    postedAt: '3 days ago'
  }
]

export default function JobsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')

  const filteredJobs = mockJobs.filter(job =>
    job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    job.company.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 dark:text-white">Job Search</h1>

        {/* Search Bar */}
        <div className="flex gap-4 mb-8">
          <SketchInput
            type="text"
            placeholder="Search jobs, companies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1"
          />
          <SketchInput
            type="text"
            placeholder="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-48"
          />
          <SketchButton variant="primary">Search</SketchButton>
        </div>

        {/* Quick Filters */}
        <div className="flex gap-2 mb-6">
          <Link href="/dashboard/jobs/saved">
            <SketchButton variant="secondary">Saved Jobs</SketchButton>
          </Link>
          <Link href="/dashboard/jobs/matches">
            <SketchButton variant="secondary">AI Matches</SketchButton>
          </Link>
        </div>

        {/* Job Listings */}
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <Link key={job.id} href={`/dashboard/jobs/${job.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer dark:bg-gray-800 dark:border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-xl dark:text-white">{job.title}</CardTitle>
                    <p className="text-gray-600 dark:text-gray-400">{job.company}</p>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      {job.matchScore}% Match
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>📍 {job.location}</span>
                    <span>💰 {job.salary}</span>
                    <span>🕐 {job.postedAt}</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            No jobs found matching your criteria.
          </div>
        )}
      </div>
    </div>
  )
}
