'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  User, Briefcase, GraduationCap, Star, Target,
  ChevronRight, Loader2, CheckCircle2, Circle, Rocket
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { getPersona, type Persona } from '@/lib/api/persona'

interface SectionInfo {
  key: string
  title: string
  description: string
  href: string
  icon: React.ElementType
  color: string
  bgColor: string
  getStatus: (persona: Persona) => { count: number; label: string; complete: boolean }
}

const sections: SectionInfo[] = [
  {
    key: 'basic',
    title: 'Basic Info',
    description: 'Name, contact details, location & work preferences',
    href: '/dashboard/persona/basic',
    icon: User,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-900/40',
    getStatus: (p) => {
      const filled = [p.full_name, p.email, p.location_city, p.location_country].filter(Boolean).length
      return { count: filled, label: `${filled}/4 fields`, complete: filled >= 2 }
    },
  },
  {
    key: 'experience',
    title: 'Experience',
    description: 'Work history, roles & achievements',
    href: '/dashboard/persona/experience',
    icon: Briefcase,
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/40',
    getStatus: (p) => {
      const count = p.experiences?.length || 0
      return { count, label: count === 0 ? 'Not started' : `${count} position${count !== 1 ? 's' : ''}`, complete: count > 0 }
    },
  },
  {
    key: 'education',
    title: 'Education',
    description: 'Degrees, certifications & training',
    href: '/dashboard/persona/education',
    icon: GraduationCap,
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-900/40',
    getStatus: (p) => {
      const count = p.educations?.length || 0
      return { count, label: count === 0 ? 'Not started' : `${count} entr${count !== 1 ? 'ies' : 'y'}`, complete: count > 0 }
    },
  },
  {
    key: 'skills',
    title: 'Skills',
    description: 'Technical skills, tools & proficiencies',
    href: '/dashboard/persona/skills',
    icon: Star,
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/40',
    getStatus: (p) => {
      const count = p.skills?.length || 0
      return { count, label: count === 0 ? 'Not started' : `${count} skill${count !== 1 ? 's' : ''}`, complete: count > 0 }
    },
  },
  {
    key: 'preferences',
    title: 'Career Preferences',
    description: 'Target roles, industries & salary expectations',
    href: '/dashboard/persona/preferences',
    icon: Target,
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/40',
    getStatus: (p) => {
      const pref = p.career_preference
      const filled = pref ? [pref.target_titles?.length, pref.target_industries?.length].filter(v => v && v > 0).length : 0
      return { count: filled, label: filled === 0 ? 'Not started' : `${filled}/2 configured`, complete: filled > 0 }
    },
  },
]

export default function PersonaBuilderPage() {
  const [persona, setPersona] = useState<Persona | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPersona()
  }, [])

  const loadPersona = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getPersona()
      setPersona(data)
    } catch (err) {
      setError('Failed to load persona. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const completedSections = persona
    ? sections.filter(s => s.getStatus(persona).complete).length
    : 0
  const completenessPercent = Math.round((completedSections / sections.length) * 100)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-ink-blue mx-auto mb-4" />
          <p className="text-lg font-handwritten text-pencil-black/60">Loading your persona...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-16 h-16 wobble bg-marker-red flex items-center justify-center">
          <Rocket className="w-8 h-8 text-white" strokeWidth={2.5} />
        </div>
        <div>
          <h1 className="text-3xl font-marker text-pencil-black">
            Persona Builder
          </h1>
          <p className="text-lg font-handwritten text-pencil-black/60">
            Build your professional identity — the AI uses this to craft perfect applications
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg border-2 border-red-300 font-handwritten">
          ⚠️ {error}
        </div>
      )}

      {/* Completeness Bar */}
      <Card className="mb-8 border-2 border-pencil-black/20">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-lg font-marker text-pencil-black">
              Profile Completeness
            </span>
            <span className="text-2xl font-marker text-ink-blue">
              {completenessPercent}%
            </span>
          </div>
          <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden border border-pencil-black/10">
            <div
              className="h-full bg-gradient-to-r from-marker-red via-yellow-400 to-green-500 transition-all duration-700 ease-out rounded-full"
              style={{ width: `${completenessPercent}%` }}
            />
          </div>
          <p className="text-sm font-handwritten text-pencil-black/50 mt-2">
            {completedSections} of {sections.length} sections completed — {completenessPercent === 100 ? '🎉 You\'re all set!' : 'keep going!'}
          </p>
        </CardContent>
      </Card>

      {/* Section Cards */}
      <div className="space-y-4">
        {sections.map((section) => {
          const status = persona ? section.getStatus(persona) : { count: 0, label: 'Not started', complete: false }
          const Icon = section.icon

          return (
            <Link key={section.key} href={section.href}>
              <Card className="border-2 border-pencil-black/10 hover:border-ink-blue hover:shadow-lg transition-all duration-200 cursor-pointer group mb-4">
                <CardContent className="py-5 px-6">
                  <div className="flex items-center gap-5">
                    {/* Icon */}
                    <div className={`w-14 h-14 wobble-sm ${section.bgColor} flex items-center justify-center shrink-0 group-hover:rotate-3 transition-transform`}>
                      <Icon className={`w-7 h-7 ${section.color}`} strokeWidth={2.5} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-xl font-marker text-pencil-black group-hover:text-ink-blue transition-colors">
                          {section.title}
                        </h3>
                        {status.complete ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-300 shrink-0" />
                        )}
                      </div>
                      <p className="text-sm font-handwritten text-pencil-black/50">
                        {section.description}
                      </p>
                    </div>

                    {/* Status Badge */}
                    <div className="flex items-center gap-3 shrink-0">
                      <span className={`text-sm font-handwritten px-3 py-1 rounded-full ${status.complete
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-500 border border-gray-200'
                        }`}>
                        {status.label}
                      </span>
                      <ChevronRight className="w-5 h-5 text-pencil-black/30 group-hover:text-ink-blue group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Tip */}
      <div className="mt-8 p-4 bg-blue-50 border-2 border-dashed border-blue-200 rounded-lg">
        <p className="text-sm font-handwritten text-blue-700">
          💡 <strong>Tip:</strong> The more complete your persona, the better the AI can tailor your applications.
          Start with Basic Info and Skills — those have the biggest impact!
        </p>
      </div>
    </div>
  )
}
