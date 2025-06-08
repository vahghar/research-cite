import { Header } from "./components/header"
import { PricingSection } from "./components/pricing-section"
import { CTASection } from "./components/cta-section"
import { HeroSection } from "./components/hero-section"
import { HowItWorksSection } from "./components/how-it-works"
import { FeaturesSection } from "./components/features-section"
import { Footer } from "./components/footer"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <PricingSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}
