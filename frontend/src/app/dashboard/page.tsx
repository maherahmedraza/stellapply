<<<<<<< HEAD
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function Page() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Welcome to Stellapply</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Manage your job applications.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Resumes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Manage your resume versions.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Search and save relevant jobs.</p>
          </CardContent>
        </Card>
=======
import { SketchCard } from "@/components/ui/hand-drawn"
import { Rocket, FileText, Briefcase, Plus } from "lucide-react"

export default function Page() {
  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-5xl font-handwritten font-bold text-pencil-black mb-2 flex items-center gap-3">
            Welcome, Space Cadet! <Rocket className="w-10 h-10 text-ink-blue animate-bounce" />
          </h1>
          <p className="text-2xl font-handwritten text-pencil-black/60 italic">Your cosmic career journey continues here...</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <SketchCard decoration="tape" className="bg-white">
          <div className="flex flex-col h-full space-y-4">
            <div className="flex items-center gap-3">
              <Briefcase className="w-8 h-8 text-ink-blue" />
              <h2 className="text-3xl font-handwritten font-bold">Applications</h2>
            </div>
            <p className="text-xl font-handwritten text-pencil-black/70 flex-grow">
              You have 5 pending applications. Time to check the radar!
            </p>
            <div className="pt-4 border-t-2 border-pencil-black/10 border-dashed">
              <p className="text-lg font-handwritten font-bold text-marker-red">Next Step: Interview prep</p>
            </div>
          </div>
        </SketchCard>

        <SketchCard decoration="tack" color="yellow">
          <div className="flex flex-col h-full space-y-4">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-marker-red" />
              <h2 className="text-3xl font-handwritten font-bold">Resumes</h2>
            </div>
            <p className="text-xl font-handwritten text-pencil-black/70 flex-grow">
              Your "Senior Role" resume is getting a lot of traction!
            </p>
            <button className="mt-4 flex items-center justify-center gap-2 border-2 border-pencil-black p-2 wobble hover:bg-pencil-black hover:text-white transition-colors font-handwritten font-bold">
              <Plus className="w-5 h-5" /> New Version
            </button>
          </div>
        </SketchCard>

        <SketchCard decoration="tape" className="bg-white">
          <div className="flex flex-col h-full space-y-4">
            <div className="flex items-center gap-3">
              <Rocket className="w-8 h-8 text-ink-blue" />
              <h2 className="text-3xl font-handwritten font-bold">Job Matches</h2>
            </div>
            <p className="text-xl font-handwritten text-pencil-black/70 flex-grow">
              Found 12 new jobs that match your DNA perfectly.
            </p>
            <p className="text-lg font-handwritten text-ink-blue font-bold cursor-pointer hover:underline underline-offset-4 decoration-wavy">
              View all matches &rarr;
            </p>
          </div>
        </SketchCard>
>>>>>>> feature/resume-upload-gdpr-compliance
      </div>
    </div>
  )
}
