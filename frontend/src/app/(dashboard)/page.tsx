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
      </div>
    </div>
  )
}
