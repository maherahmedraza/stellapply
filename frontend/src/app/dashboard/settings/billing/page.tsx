<<<<<<< HEAD
'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, CreditCard, Check, Crown, Zap, Star, Download, Loader2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { SketchButton } from "@/components/ui/hand-drawn"
import { getBillingInfo, changePlan, cancelSubscription, type BillingInfo } from '@/lib/api/persona'

export default function BillingPage() {
  const [billing, setBilling] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    loadBilling()
  }, [])

  const loadBilling = async () => {
    setLoading(true)
    try {
      const data = await getBillingInfo()
      setBilling(data)
    } catch (err) {
      console.error('Error loading billing:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleChangePlan = async (planId: string) => {
    setUpgrading(planId)
    setError(null)
    try {
      const result = await changePlan(planId)
      setSuccess(result.message)
      await loadBilling() // Refresh data
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to change plan')
    } finally {
      setUpgrading(null)
    }
  }

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return
    setError(null)
    try {
      const result = await cancelSubscription()
      setSuccess(result.message)
      await loadBilling()
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to cancel subscription')
    }
  }

  const getPlanIcon = (tier: string) => {
    switch (tier) {
      case 'free': return <Star className="w-6 h-6 text-gray-400" />
      case 'plus': return <Zap className="w-6 h-6 text-blue-500" />
      case 'pro': return <Crown className="w-6 h-6 text-yellow-500" />
      default: return <Star className="w-6 h-6" />
    }
  }

  if (loading) {
    return (
      <div className="p-6 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  const currentTier = billing?.current_plan.tier || 'free'

  return (
    <div className="p-6 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <Link href="/dashboard/settings" className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
            <CreditCard className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold dark:text-white">Billing & Plans</h1>
            <p className="text-gray-600 dark:text-gray-400">Manage your subscription and payment</p>
          </div>
        </div>

        {success && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
            ✓ {success}
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
            ⚠️ {error}
          </div>
        )}

        {/* Current Plan */}
        <Card className="dark:bg-gray-800 dark:border-gray-700 mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="dark:text-white flex items-center gap-2">
                  <Crown className="w-5 h-5 text-yellow-500" />
                  Current Plan: <span className="text-blue-600 dark:text-blue-400">{billing?.current_plan.tier_display}</span>
                </CardTitle>
                <CardDescription className="dark:text-gray-400">
                  {billing?.current_plan.next_billing_date
                    ? `Next billing date: ${billing.current_plan.next_billing_date} • €${billing.current_plan.price_monthly}/month`
                    : 'Free forever'}
                </CardDescription>
              </div>
              {currentTier !== 'free' && (
                <SketchButton onClick={handleCancel} variant="secondary" className="text-red-600 border-red-300">
                  Cancel Subscription
                </SketchButton>
              )}
            </div>
          </CardHeader>
        </Card>

        {/* Available Plans */}
        <h2 className="text-xl font-bold dark:text-white mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {billing?.available_plans.map((plan) => (
            <Card
              key={plan.tier}
              className={`dark:bg-gray-800 dark:border-gray-700 ${plan.is_current ? 'border-blue-400 ring-2 ring-blue-200 dark:ring-blue-800' : ''
                } ${plan.tier === 'plus' ? 'relative' : ''}`}
            >
              {plan.tier === 'plus' && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}
              <CardHeader className="text-center">
                {getPlanIcon(plan.tier)}
                <CardTitle className="dark:text-white mt-2">{plan.name}</CardTitle>
                <div className="text-3xl font-bold dark:text-white">
                  {plan.price_monthly > 0 ? `€${plan.price_monthly}` : 'Free'}
                  {plan.price_monthly > 0 && <span className="text-sm font-normal text-gray-500">/month</span>}
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                {plan.is_current ? (
                  <div className="text-center text-blue-600 dark:text-blue-400 font-medium">
                    Current Plan
                  </div>
                ) : (
                  <SketchButton
                    onClick={() => handleChangePlan(plan.tier)}
                    variant={plan.tier === 'plus' ? 'primary' : 'secondary'}
                    className="w-full"
                    disabled={upgrading === plan.tier}
                  >
                    {upgrading === plan.tier ? (
                      <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Processing...</>
                    ) : (
                      currentTier === 'free' || plan.price_monthly > (billing?.current_plan.price_monthly || 0)
                        ? 'Upgrade'
                        : 'Downgrade'
                    )}
                  </SketchButton>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Payment Method */}
        {billing?.payment_method && (
          <Card className="dark:bg-gray-800 dark:border-gray-700 mb-8">
            <CardHeader>
              <CardTitle className="dark:text-white">Payment Method</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 dark:bg-blue-900 px-3 py-1 rounded text-sm font-bold uppercase">
                    {billing.payment_method.type}
                  </div>
                  <span className="text-gray-600 dark:text-gray-300">
                    •••• •••• •••• {billing.payment_method.last4}
                  </span>
                  <span className="text-gray-400 text-sm">
                    Expires {billing.payment_method.expiry}
                  </span>
                </div>
                <SketchButton variant="secondary">Update Card</SketchButton>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Billing History */}
        {billing?.invoices && billing.invoices.length > 0 && (
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="dark:text-white">Billing History</CardTitle>
            </CardHeader>
            <CardContent>
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-500 dark:text-gray-400 text-sm border-b dark:border-gray-700">
                    <th className="pb-2">Invoice</th>
                    <th className="pb-2">Date</th>
                    <th className="pb-2">Amount</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {billing.invoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b dark:border-gray-700">
                      <td className="py-3 font-medium dark:text-white">{invoice.id}</td>
                      <td className="py-3 text-gray-600 dark:text-gray-300">{invoice.date}</td>
                      <td className="py-3 dark:text-white">€{invoice.amount.toFixed(2)}</td>
                      <td className="py-3">
                        <span className="text-green-600 dark:text-green-400 capitalize">{invoice.status}</span>
                      </td>
                      <td className="py-3">
                        <button className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 text-sm">
                          <Download className="w-4 h-4" /> PDF
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
=======
"use client";

import React from "react";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { CreditCard, Rocket, Check, Zap, Star, Crown } from "lucide-react";
import Link from "next/link";

const plans = [
  {
    id: "free",
    name: "Free",
    price: 0,
    icon: Star,
    features: [
      "Basic resume builder",
      "3 resume downloads/month",
      "Manual applications only",
      "Basic job matching",
    ],
    color: "bg-muted-paper",
    current: false,
  },
  {
    id: "plus",
    name: "Plus",
    price: 19,
    icon: Zap,
    features: [
      "AI resume tailoring",
      "Unlimited downloads",
      "5 auto-applies/day",
      "20 auto-applies/week",
      "ATS optimization",
    ],
    color: "bg-ink-blue/10",
    current: true,
  },
  {
    id: "pro",
    name: "Pro",
    price: 39,
    icon: Rocket,
    features: [
      "Everything in Plus",
      "8 auto-applies/day",
      "40 auto-applies/week",
      "Cover letter generation",
      "Interview prep",
      "Priority support",
    ],
    color: "bg-postit-yellow",
    current: false,
  },
  {
    id: "premium",
    name: "Premium",
    price: 79,
    icon: Crown,
    features: [
      "Everything in Pro",
      "20 auto-applies/day",
      "100 auto-applies/week",
      "LinkedIn automation",
      "Dedicated success manager",
      "Custom integrations",
    ],
    color: "bg-marker-red/10",
    current: false,
  },
];

export default function BillingPage() {
  const currentPlan = plans.find(p => p.current);

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <header className="mb-8">
        <Link href="/dashboard/settings" className="text-ink-blue hover:underline font-handwritten mb-4 block">
          ← Back to Settings
        </Link>
        <h1 className="text-5xl font-marker text-pencil-black mb-2 -rotate-1">Billing & Plans</h1>
        <p className="text-xl font-handwritten text-pencil-black/70">
          Upgrade your career sketching toolkit.
        </p>
      </header>

      {/* Current Plan */}
      <SketchCard decoration="tape" className="p-6 bg-ink-blue text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <CreditCard className="w-10 h-10" />
            <div>
              <p className="font-handwritten text-lg opacity-80">Current Plan</p>
              <h2 className="text-4xl font-marker">{currentPlan?.name} Plan</h2>
            </div>
          </div>
          <div className="text-right">
            <p className="text-5xl font-marker">${currentPlan?.price}</p>
            <p className="font-handwritten opacity-80">/month</p>
          </div>
        </div>
      </SketchCard>

      {/* Usage Stats */}
      <div className="grid grid-cols-3 gap-4">
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-3xl font-marker text-ink-blue">12/20</p>
          <p className="font-handwritten text-pencil-black/60">Auto-applies this week</p>
        </SketchCard>
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-3xl font-marker text-marker-red">47</p>
          <p className="font-handwritten text-pencil-black/60">Resumes generated</p>
        </SketchCard>
        <SketchCard decoration="none" className="p-4 text-center">
          <p className="text-3xl font-marker text-pencil-black">18 days</p>
          <p className="font-handwritten text-pencil-black/60">Until renewal</p>
        </SketchCard>
      </div>

      {/* Plan Comparison */}
      <h2 className="text-3xl font-marker mt-12 mb-6">Compare Plans</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((plan) => {
          const Icon = plan.icon;
          return (
            <SketchCard
              key={plan.id}
              decoration="none"
              className={`p-6 ${plan.color} ${plan.current ? "border-4 border-ink-blue" : ""}`}
            >
              <div className="flex items-center gap-2 mb-4">
                <Icon className="w-6 h-6" />
                <h3 className="text-2xl font-marker">{plan.name}</h3>
              </div>
              <p className="text-4xl font-marker mb-4">
                ${plan.price}
                <span className="text-lg font-handwritten text-pencil-black/60">/mo</span>
              </p>
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 font-handwritten">
                    <Check className="w-4 h-4 mt-1 text-ink-blue flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              {plan.current ? (
                <div className="text-center font-marker text-ink-blue border-2 border-ink-blue py-2 wobble">
                  Current Plan
                </div>
              ) : (
                <SketchButton
                  variant={plan.price > (currentPlan?.price || 0) ? "primary" : "secondary"}
                  className="w-full"
                >
                  {plan.price > (currentPlan?.price || 0) ? "Upgrade" : "Downgrade"}
                </SketchButton>
              )}
            </SketchCard>
          );
        })}
      </div>

      {/* Payment Method */}
      <SketchCard decoration="none" className="p-6 mt-8">
        <h3 className="text-2xl font-marker mb-4">Payment Method</h3>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-10 bg-pencil-black/10 wobble flex items-center justify-center font-marker">
              VISA
            </div>
            <div>
              <p className="font-handwritten text-lg">•••• •••• •••• 4242</p>
              <p className="font-handwritten text-pencil-black/60">Expires 12/27</p>
            </div>
          </div>
          <SketchButton variant="secondary">Update</SketchButton>
        </div>
      </SketchCard>
    </div>
  );
>>>>>>> feature/resume-upload-gdpr-compliance
}
