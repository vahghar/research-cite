import { Button } from "@/components/ui/button"
import { ArrowRight, FileText, LinkIcon, GraduationCap, Baby } from "lucide-react"
import Link from "next/link"

export function HeroSection() {
  return (
    <section className="py-20 md:py-32 bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-8 inline-flex items-center rounded-full border px-4 py-2 text-sm">
            <span className="mr-2">🎓</span>
            Transform your academic research workflow
          </div>

          <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            Instant Summaries from
            <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              {" "}
              Research Papers
            </span>
          </h1>

          <p className="mb-8 text-xl text-muted-foreground sm:text-2xl max-w-2xl mx-auto">
            Upload research papers, academic articles, or paste research links to get AI-powered summaries, references, and citations in seconds. Perfect for researchers, students, and academics.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="text-lg px-8" asChild>
              <Link href="/signup">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>

          {/* Feature Icons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <span>Research Papers</span>
            </div>
            <div className="flex items-center gap-2">
              <LinkIcon className="h-5 w-5 text-primary" />
              <span>Academic Articles</span>
            </div>
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary" />
              <span>Smart Citations</span>
            </div>
            <div className="flex items-center gap-2">
              <Baby className="h-5 w-5 text-primary" />
              <span>ELI5 Explanations</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
