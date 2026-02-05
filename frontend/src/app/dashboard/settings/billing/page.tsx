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
}
