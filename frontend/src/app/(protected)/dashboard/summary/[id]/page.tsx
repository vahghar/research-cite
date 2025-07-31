"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ArrowLeft, FileText, Calendar, User, ExternalLink, Download, Share2 } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface SummaryData {
  id: number
  document_id: number
  introduction: string
  methods: string
  results: string
  conclusion: string
  eli5_summary: string | null
}

interface DocumentData {
  id: number
  original_filename: string
  source_url: string | null
  created_at: string
  status: string
}

interface CitationData {
  id: number
  document_id: number
  raw_bibtex: string
  apa_text: string | null
  doi: string | null
  title: string | null
  authors: string | null
  year: string | null
}

export default function SummaryDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [document, setDocument] = useState<DocumentData | null>(null)
  const [citations, setCitations] = useState<CitationData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const documentId = params.id as string

  useEffect(() => {
    const fetchSummaryData = async () => {
      try {
        setLoading(true)
        const token = localStorage.getItem("access_token")
        
        if (!token) {
          setError("Authentication required")
          return
        }

        // Fetch document details
        const docResponse = await fetch(`http://localhost:8000/documents/${documentId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (!docResponse.ok) {
          throw new Error("Document not found")
        }

        const docData = await docResponse.json()
        setDocument(docData)

        // Fetch summary
        const summaryResponse = await fetch(`http://localhost:8000/documents/${documentId}/summary`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (!summaryResponse.ok) {
          throw new Error("Summary not found")
        }

        const summaryData = await summaryResponse.json()
        setSummary(summaryData)

        // Fetch citations
        const citationsResponse = await fetch(`http://localhost:8000/documents/${documentId}/citations`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (citationsResponse.ok) {
          const citationsData = await citationsResponse.json()
          setCitations(citationsData)
        }

      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load summary")
      } finally {
        setLoading(false)
      }
    }

    if (documentId) {
      fetchSummaryData()
    }
  }, [documentId])

  const handleGenerateELI5 = async () => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await fetch(`http://localhost:8000/documents/${documentId}/eli5`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        const updatedSummary = await response.json()
        setSummary(updatedSummary)
      } else {
        setError("Failed to generate ELI5 summary")
      }
    } catch (err) {
      setError("Failed to generate ELI5 summary")
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading summary...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button 
          onClick={() => router.back()} 
          variant="outline" 
          className="mt-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    )
  }

  if (!summary || !document) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert>
          <AlertDescription>Summary not found</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <Button 
          onClick={() => router.back()} 
          variant="ghost" 
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">
              {document.original_filename || "Research Paper Summary"}
            </h1>
            <div className="flex items-center gap-4 text-muted-foreground">
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                {formatDate(document.created_at)}
              </div>
              <div className="flex items-center">
                <FileText className="h-4 w-4 mr-1" />
                PDF Document
              </div>
              <Badge variant="secondary">{document.status}</Badge>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="summary" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="citations">Citations ({citations.length})</TabsTrigger>
          <TabsTrigger value="eli5">ELI5</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="space-y-6">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Introduction</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <p className="text-sm leading-relaxed">
                    {summary.introduction || "No introduction available."}
                  </p>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Methods</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <p className="text-sm leading-relaxed">
                    {summary.methods || "No methods available."}
                  </p>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Results</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <p className="text-sm leading-relaxed">
                    {summary.results || "No results available."}
                  </p>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Conclusion</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <p className="text-sm leading-relaxed">
                    {summary.conclusion || "No conclusion available."}
                  </p>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="citations" className="space-y-4">
          {citations.length > 0 ? (
            <div className="space-y-4">
              {citations.map((citation, index) => (
                <Card key={citation.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">
                          {citation.title || `Citation ${index + 1}`}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {citation.authors && (
                            <div className="flex items-center mb-2">
                              <User className="h-4 w-4 mr-1" />
                              {citation.authors}
                            </div>
                          )}
                          {citation.year && (
                            <Badge variant="outline" className="mr-2">
                              {citation.year}
                            </Badge>
                          )}
                          {citation.doi && (
                            <Badge variant="outline">
                              DOI: {citation.doi}
                            </Badge>
                          )}
                        </CardDescription>
                      </div>
                      {citation.doi && (
                        <Button variant="ghost" size="sm" asChild>
                          <a 
                            href={`https://doi.org/${citation.doi}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {citation.apa_text && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">APA Citation:</h4>
                          <p className="text-sm text-muted-foreground">{citation.apa_text}</p>
                        </div>
                      )}
                      <div>
                        <h4 className="font-medium text-sm mb-1">BibTeX:</h4>
                        <ScrollArea className="h-[100px]">
                          <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                            {citation.raw_bibtex}
                          </pre>
                        </ScrollArea>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No citations found for this document.</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="eli5" className="space-y-4">
          {summary.eli5_summary ? (
            <Card>
              <CardHeader>
                <CardTitle>Explain Like I'm 5</CardTitle>
                <CardDescription>
                  A simplified explanation of the research paper
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <p className="text-sm leading-relaxed">
                    {summary.eli5_summary}
                  </p>
                </ScrollArea>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-muted-foreground">
                  <p className="mb-4">ELI5 summary not yet generated.</p>
                  <Button onClick={handleGenerateELI5}>
                    Generate ELI5 Summary
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>


      </Tabs>
    </div>
  )
} 