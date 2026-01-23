"use client"

import Link from "next/link"
import { useTheme } from "@/context/theme-context"
import { Button } from "@/components/ui/button"
import { Sun, Moon, ArrowRight, Upload, BarChart3, Download, Sparkles } from "lucide-react"

const features = [
  {
    icon: Upload,
    title: "Easy Upload",
    description: "Drag and drop CSV or Excel files for instant processing",
  },
  {
    icon: Sparkles,
    title: "AI Preprocessing",
    description: "Automatically clean and prepare data for machine learning",
  },
  {
    icon: BarChart3,
    title: "Rich Insights",
    description: "Visualize statistics, distributions, and correlations",
  },
  {
    icon: Download,
    title: "Quick Export",
    description: "Download cleaned datasets in your preferred format",
  },
]

export default function HomePage() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-bold text-primary-foreground">P</span>
            </div>
            <span className="text-xl font-bold tracking-tight">Prepit</span>
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild>
              <Link href="/signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main>
        <section className="py-20 lg:py-32">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-balance max-w-4xl mx-auto">
              AI-Powered Data Preprocessing for Machine Learning
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
              Transform your raw data into ML-ready datasets in seconds. Upload your CSV
              or Excel files and let AI handle the cleaning, analysis, and preparation.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" asChild>
                <Link href="/signup">
                  Start Preprocessing
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/login">Sign in to Dashboard</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight">
                Everything you need for data preprocessing
              </h2>
              <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
                Prepit handles the tedious work of cleaning and preparing your data,
                so you can focus on building machine learning models.
              </p>
            </div>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="text-center p-6 rounded-xl border border-border bg-card"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary mx-auto">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-4 font-semibold">{feature.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-4">
            <div className="bg-primary text-primary-foreground rounded-2xl p-8 lg:p-12 text-center">
              <h2 className="text-2xl lg:text-3xl font-bold">
                Ready to preprocess your data?
              </h2>
              <p className="mt-4 text-primary-foreground/80 max-w-xl mx-auto">
                Join thousands of data scientists who use Prepit to prepare their
                datasets for machine learning.
              </p>
              <Button
                size="lg"
                variant="secondary"
                className="mt-8"
                asChild
              >
                <Link href="/signup">
                  Get Started for Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded bg-primary">
                <span className="text-xs font-bold text-primary-foreground">P</span>
              </div>
              <span className="text-sm text-muted-foreground">
                Prepit - AI Data Preprocessing
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Built for the machine learning community
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
