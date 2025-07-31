"use client"
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, FileText, Calendar, MoreVertical, Trash2, Download, Eye } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export function PreviousSummariesSection() {
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState("")
  const [summaries, setSummaries] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set())

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true)
        const token = localStorage.getItem("access_token") // assuming you store JWT in localStorage
        const response = await fetch("http://localhost:8000/documents/", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        const docs = await response.json()

        // Map documents to summary card format
        const formattedSummaries = await Promise.all(
          docs.map(async (doc: any) => {
            let summaryText = ""
            if (doc.status === "COMPLETED") {
              try {
                const summaryResponse = await fetch(`http://localhost:8000/documents/${doc.id}/summary`, {
                  method: "GET",
                  headers: { Authorization: `Bearer ${token}` },
                })
                if (summaryResponse.ok) {
                  const summaryData = await summaryResponse.json()
                  // Construct summary text from the available fields
                  const summaryParts = [
                    summaryData.introduction,
                    summaryData.methods,
                    summaryData.results,
                    summaryData.conclusion
                  ].filter(part => part && part.trim() !== "")
                  
                  summaryText = summaryParts.length > 0 
                    ? summaryParts.join(" ") 
                    : "Summary not available."
                } else {
                  summaryText = "Summary not available."
                }
              } catch (e) {
                summaryText = "Summary not available."
              }
            } else {
              summaryText = "Processing..."
            }

            return {
              id: doc.id,
              title: doc.original_filename || doc.source_url || "Untitled Document",
              authors: [], // extend your API later to include authors if needed
              date: doc.created_at,
              tags: [], // extend your API later to include tags if needed
              summary: summaryText,
            }
          })
        )

        setSummaries(formattedSummaries)
      } catch (error) {
        console.error("Error fetching documents:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  const handleDelete = async (docId: number) => {
    // Add confirmation dialog
    const isConfirmed = window.confirm("Are you sure you want to delete this document? This action cannot be undone.")
    if (!isConfirmed) {
      return
    }

    // Set loading state for this specific document
    setDeletingIds(prev => new Set(prev).add(docId))

    try {
      const token = localStorage.getItem("access_token")
      if (!token) {
        console.error("No access token found")
        return
      }

      const response = await fetch(`http://localhost:8000/documents/${docId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setSummaries((prevSummaries) => prevSummaries.filter((summary) => summary.id !== docId))
        console.log("Document deleted successfully")
        // You could add a success toast notification here
      } else {
        const errorData = await response.json().catch(() => ({}))
        console.error("Failed to delete document:", response.status, errorData)
        alert(`Failed to delete document: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error("Error deleting document:", error)
      alert("Error deleting document. Please try again.")
    } finally {
      // Clear loading state
      setDeletingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(docId)
        return newSet
      })
    }
  }

  const handleViewSummary = (summaryId: number) => {
    router.push(`/dashboard/summary/${summaryId}`)
  }

  const filteredSummaries = summaries.filter(
    (summary) =>
      summary.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      summary.authors.some((author: string) => author.toLowerCase().includes(searchTerm.toLowerCase())) ||
      summary.tags.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase())),
  )

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  return (
    <Card className="h-fit">
      <CardHeader>
        <CardTitle>Previous Summaries</CardTitle>
        <CardDescription>Your research paper analysis history</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search research papers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Summary List */}
        <ScrollArea className="h-[600px]">
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">Loading documents...</div>
            ) : (
              filteredSummaries.map((summary) => (
                <Card 
                  key={summary.id} 
                  className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => handleViewSummary(summary.id)}
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1 flex-1">
                        <h4 className="font-medium text-sm leading-tight line-clamp-2">{summary.title}</h4>
                        <p className="text-xs text-muted-foreground">{summary.authors.join(", ")}</p>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0"
                            onClick={event => event.stopPropagation()}
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleViewSummary(summary.id)}>
                            <Eye className="mr-2 h-4 w-4" />
                            View
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="mr-2 h-4 w-4" />
                            Export
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-destructive" 
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(summary.id)
                            }}
                            disabled={deletingIds.has(summary.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            {deletingIds.has(summary.id) ? "Deleting..." : "Delete"}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    <p className="text-xs text-muted-foreground line-clamp-2">{summary.summary}</p>

                    <div className="flex flex-wrap gap-1">
                      {summary.tags.slice(0, 2).map((tag: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {summary.tags.length > 2 && (
                        <Badge variant="secondary" className="text-xs">
                          +{summary.tags.length - 2}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(summary.date)}
                      </div>
                      <div className="flex items-center">
                        <FileText className="h-3 w-3 mr-1" />
                        PDF
                      </div>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </ScrollArea>

        {!loading && filteredSummaries.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No summaries found</p>
            <p className="text-xs">Try adjusting your search terms</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
