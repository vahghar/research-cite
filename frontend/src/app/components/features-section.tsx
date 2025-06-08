import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, LinkIcon, Quote, Zap, Shield, Clock } from "lucide-react"

const features = [
  {
    icon: FileText,
    title: "PDF Processing",
    description:
      "Upload any PDF document and get instant AI-powered summaries with key insights extracted automatically.",
  },
  {
    icon: LinkIcon,
    title: "Link Analysis",
    description:
      "Paste any web link and receive comprehensive summaries of articles, research papers, and web content.",
  },
  {
    icon: Quote,
    title: "Smart Citations",
    description:
      "Automatically generate properly formatted citations and references for academic and professional use.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Get results in seconds, not hours. Our AI processes documents and links at incredible speed.",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your documents are processed securely and never stored permanently. Complete privacy guaranteed.",
  },
  {
    icon: Clock,
    title: "Save Time",
    description: "Reduce research time by 90%. Focus on analysis instead of reading through lengthy documents.",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-20  bg-muted/30">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">Powerful Features for Modern Research</h2>
          <p className="text-lg text-muted-foreground">
            Everything you need to streamline your research and content analysis workflow
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card key={index} className="border-0 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
