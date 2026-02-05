<<<<<<< HEAD
'use client'

import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const settingsSections = [
  {
    title: 'Data Control',
    description: 'Manage your data, export, or delete your account',
    href: '/dashboard/settings/data-control',
    icon: '🔒'
  },
  {
    title: 'Preferences',
    description: 'Customize your job search preferences',
    href: '/dashboard/settings/preferences',
    icon: '⚙️'
  },
  {
    title: 'Notifications',
    description: 'Configure email and push notifications',
    href: '/dashboard/settings/notifications',
    icon: '🔔'
  },
  {
    title: 'Automation',
    description: 'Set up auto-apply and job alerts',
    href: '/dashboard/settings/automation',
    icon: '🤖'
  },
  {
    title: 'Billing',
    description: 'Manage your subscription and payment',
    href: '/dashboard/settings/billing',
    icon: '💳'
  }
]

export default function SettingsPage() {
  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Manage your account settings and preferences
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {settingsSections.map((section) => (
            <Link key={section.href} href={section.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{section.icon}</span>
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
      </div>
    </div>
  )
=======
"use client";

import Link from "next/link";
import { SketchCard } from "@/components/ui/hand-drawn";
import { Bell, Shield, Zap, CreditCard, User } from "lucide-react";

const settingsLinks = [
  {
    href: "/dashboard/settings/preferences",
    title: "Preferences",
    description: "Customize your job search preferences",
    icon: User,
    color: "bg-ink-blue/10",
  },
  {
    href: "/dashboard/settings/notifications",
    title: "Notifications",
    description: "Manage email and push alerts",
    icon: Bell,
    color: "bg-postit-yellow",
  },
  {
    href: "/dashboard/settings/privacy",
    title: "Privacy",
    description: "Control your data and visibility",
    icon: Shield,
    color: "bg-marker-red/10",
  },
  {
    href: "/dashboard/settings/automation",
    title: "Automation",
    description: "Configure auto-apply settings",
    icon: Zap,
    color: "bg-ink-blue/10",
  },
  {
    href: "/dashboard/settings/billing",
    title: "Billing",
    description: "Manage subscription and payments",
    icon: CreditCard,
    color: "bg-postit-yellow",
  },
];

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-5xl font-marker mb-2 -rotate-1">Settings</h1>
      <p className="text-xl font-handwritten text-pencil-black/60 mb-8">
        Tweak your cosmic experience
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {settingsLinks.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <SketchCard
                className={`${item.color} p-6 h-full hover:shadow-sketch-lg transition-all cursor-pointer group`}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 wobble bg-white border-2 border-pencil-black flex items-center justify-center group-hover:rotate-6 transition-transform">
                    <Icon className="w-6 h-6 text-pencil-black" strokeWidth={2.5} />
                  </div>
                  <div>
                    <h2 className="text-2xl font-marker mb-1 group-hover:text-ink-blue transition-colors">
                      {item.title}
                    </h2>
                    <p className="font-handwritten text-pencil-black/60">
                      {item.description}
                    </p>
                  </div>
                </div>
              </SketchCard>
            </Link>
          );
        })}
      </div>
    </div>
  );
>>>>>>> feature/resume-upload-gdpr-compliance
}
