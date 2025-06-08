import { Card, CardContent } from "@/components/ui/card"
import { Upload, Brain, FileCheck } from "lucide-react"

const steps = [
  {
    icon: Upload,
    title: "Upload or Paste",
    description: "Simply upload your PDF file or paste a link to any web content you want to analyze.",
  },
  {
    icon: Brain,
    title: "AI Processing",
    description: "Our advanced AI analyzes the content, extracting key information and insights automatically.",
  },
  {
    icon: FileCheck,
    title: "Get Results",
    description: "Receive a comprehensive summary with references, citations, and key takeaways in seconds.",
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">How Flash Digest Works</h2>
          <p className="text-lg text-muted-foreground">Get from content to insights in just three simple steps</p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <Card className="text-center border-0 shadow-sm">
                <CardContent className="pt-8 pb-8">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mx-auto mb-6">
                    <step.icon className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                </CardContent>
              </Card>

              {/* Connector Arrow */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                  <div className="w-8 h-0.5 bg-border"></div>
                  <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-border border-t-2 border-b-2 border-t-transparent border-b-transparent"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
