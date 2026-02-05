'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { SketchButton } from "@/components/ui/hand-drawn"
import { User, Briefcase, GraduationCap, Star, Target, Upload, CheckCircle, Loader2 } from 'lucide-react'

// Persona sections for navigation
const personaSections = [
  { id: 'basic', title: 'Basic Info', icon: User, description: 'Name, email, phone, location' },
  { id: 'experience', title: 'Experience', icon: Briefcase, description: 'Work history and achievements' },
  { id: 'education', title: 'Education', icon: GraduationCap, description: 'Degrees and certifications' },
  { id: 'skills', title: 'Skills', icon: Star, description: 'Technical and soft skills' },
  { id: 'preferences', title: 'Career Goals', icon: Target, description: 'Target roles and preferences' },
]

interface ParsedResumeData {
  success: boolean
  message: string
  personal_info?: {
    name?: string
    email?: string
    phone?: string
    linkedin?: string
    github?: string
    location?: string
  }
  skills?: string[]
  experience?: Array<{
    title: string
    company: string
    location?: string
    start_date?: string
    end_date?: string
    current: boolean
    highlights: string[]
  }>
  education?: Array<{
    degree: string
    school: string
    field?: string
    start_year?: string
    end_year?: string
  }>
  summary?: string
}

export default function PersonaPage() {
  const [uploadingResume, setUploadingResume] = useState(false)
  const [completeness, setCompleteness] = useState(0)
  const [parseResult, setParseResult] = useState<ParsedResumeData | null>(null)
  const [showSuccess, setShowSuccess] = useState(false)

  useEffect(() => {
    const fetchPersona = async () => {
      try {
        const token = document.cookie
          .split('; ')
          .find(row => row.startsWith('access_token='))
          ?.split('=')[1]

        if (!token) return

        const res = await fetch('http://localhost:8000/api/v1/persona/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (res.ok) {
          const data = await res.json()
          setCompleteness(data.completeness_score || 0)
        }
      } catch (err) {
        console.error("Failed to fetch persona completeness:", err)
      }
    }
    fetchPersona()
  }, [])


  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadingResume(true)
    setParseResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Get auth token from cookie
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1]

      const response = await fetch('/api/v1/resume/upload', {
        method: 'POST',
        body: formData,
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      })

      if (response.ok) {
        const data: ParsedResumeData = await response.json()
        setParseResult(data)

        if (data.success) {
          // Store parsed data in localStorage for the sub-pages to use
          localStorage.setItem('parsedPersona', JSON.stringify(data))

          // Calculate approximate completeness based on extracted data
          let score = 0
          if (data.personal_info?.name) score += 10
          if (data.personal_info?.email) score += 10
          if (data.skills && data.skills.length > 0) score += 10
          if (data.experience && data.experience.length > 0) score += 30
          if (data.education && data.education.length > 0) score += 20
          setCompleteness(Math.min(100, score))

          setShowSuccess(true)
          setTimeout(() => setShowSuccess(false), 5000)
        }
      } else {
        const errorData = await response.json()
        alert(`Failed to parse resume: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed. Make sure the backend is running and you are logged in.')
    } finally {
      setUploadingResume(false)
    }
  }

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold dark:text-white">Your Persona</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Build your professional profile for AI-powered job matching
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Profile Completeness</div>
            <div className="flex items-center gap-2">
              <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
                  style={{ width: `${completeness}%` }}
                />
              </div>
              <span className="text-lg font-bold text-green-600 dark:text-green-400">{completeness}%</span>
            </div>
          </div>
        </div>

        {/* Success Banner */}
        {showSuccess && parseResult?.success && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-700 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            <div className="flex-1">
              <p className="font-medium text-green-800 dark:text-green-200">
                Resume parsed successfully!
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">
                {parseResult.message}
                {parseResult.skills && parseResult.skills.length > 0 && (
                  <> Found skills: {parseResult.skills.slice(0, 5).join(', ')}{parseResult.skills.length > 5 ? '...' : ''}</>
                )}
              </p>
            </div>
          </div>
        )}

        {/* Resume Upload Section */}
        <Card className="mb-8 dark:bg-gray-800 dark:border-gray-700 border-dashed border-2">
          <CardContent className="p-6">
            <div className="flex items-center gap-6">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold dark:text-white">Quick Import</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Upload your resume (PDF, DOC, DOCX) and we&apos;ll extract your information automatically using AI.
                </p>
                <div className="flex gap-3 mt-4">
                  <label className="relative cursor-pointer">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={handleResumeUpload}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      disabled={uploadingResume}
                    />
                    <SketchButton
                      variant="primary"
                      disabled={uploadingResume}
                      className="pointer-events-none"
                    >
                      {uploadingResume ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                          Parsing with AI...
                        </>
                      ) : (
                        '📄 Upload Resume'
                      )}
                    </SketchButton>
                  </label>
                  <SketchButton variant="secondary">
                    Import from LinkedIn
                  </SketchButton>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Extracted Data Preview */}
        {parseResult?.success && parseResult.personal_info && (
          <Card className="mb-8 dark:bg-gray-800 dark:border-gray-700 border-blue-200 dark:border-blue-700">
            <CardHeader>
              <CardTitle className="dark:text-white text-lg flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Extracted Information
              </CardTitle>
              <CardDescription className="dark:text-gray-400">
                Review and edit in the sections below
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                {parseResult.personal_info.name && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Name:</span>
                    <p className="font-medium dark:text-white">{parseResult.personal_info.name}</p>
                  </div>
                )}
                {parseResult.personal_info.email && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Email:</span>
                    <p className="font-medium dark:text-white">{parseResult.personal_info.email}</p>
                  </div>
                )}
                {parseResult.personal_info.phone && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Phone:</span>
                    <p className="font-medium dark:text-white">{parseResult.personal_info.phone}</p>
                  </div>
                )}
                {parseResult.skills && parseResult.skills.length > 0 && (
                  <div className="col-span-2 md:col-span-4">
                    <span className="text-gray-500 dark:text-gray-400">Skills ({parseResult.skills.length}):</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {parseResult.skills.map((skill, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Persona Sections Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {personaSections.map((section) => (
            <Link key={section.id} href={`/dashboard/persona/${section.id}`}>
              <Card className="hover:shadow-lg transition-all cursor-pointer h-full dark:bg-gray-800 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <section.icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <CardTitle className="text-lg dark:text-white">
                        {section.title}
                      </CardTitle>
                      <CardDescription className="dark:text-gray-400">
                        {section.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>

        {/* AI Summary Section */}
        <Card className="mt-8 dark:bg-gray-800 dark:border-gray-700">
          <CardHeader>
            <CardTitle className="dark:text-white flex items-center gap-2">
              ✨ AI Career Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 dark:text-gray-400 italic">
              Complete your profile to generate an AI-powered career summary that helps match you with the best opportunities.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
