"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Copy, Download, Share, BookOpen, Quote, Users, Baby, Sparkles } from "lucide-react"
import { Alert } from "@/components/ui/alert"

interface SummaryRead {
    id: number;
    document_id: number;
    introduction: string;
    methods: string;
    results: string;
    conclusion: string;
    eli5_summary: string | null;
}

interface PaperRecommendation {
    title: string;
    authors: string;
    abstract: string;
    url: string;
    year: number;
}

export function CurrentSummarySection({ documentId }: { documentId: number }) {
    const [data, setData] = useState<SummaryRead | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<"introduction" | "methods" | "results" | "conclusion" | "eli5">("introduction");
    const [generatingEli5, setGeneratingEli5] = useState(false);
    const [recommendations, setRecommendations] = useState<PaperRecommendation[] | null>(null);
    const [recError, setRecError] = useState<string | null>(null);
    const [recLoading, setRecLoading] = useState(false);

    useEffect(() => {
        if (!documentId) return;

        const token = localStorage.getItem("access_token");
        fetch(`http://localhost:8000/documents/${documentId}/summary`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(async (res) => {
                if (!res.ok) {
                    const body = await res.json().catch(() => ({}));
                    throw new Error(body.detail || res.statusText);
                }
                return res.json() as Promise<SummaryRead>;
            })
            .then(setData)
            .catch((err) => {
                console.error(err);
                setError(err.message);
            });
    }, [documentId]);

    useEffect(() => {
        if (!documentId) return;
        setRecLoading(true);
        setRecError(null);
        setRecommendations(null);
        const token = localStorage.getItem("access_token");
        fetch(`http://localhost:8000/documents/${documentId}/recommendations`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(async (res) => {
                if (!res.ok) {
                    const body = await res.json().catch(() => ({}));
                    throw new Error(body.detail || res.statusText);
                }
                return res.json();
            })
            .then((data) => setRecommendations(data.recommendations || []))
            .catch((err) => {
                setRecError(err.message);
            })
            .finally(() => setRecLoading(false));
    }, [documentId]);

    const generateEli5 = async () => {
        if (!documentId) return;
        
        setGeneratingEli5(true);
        try {
            const token = localStorage.getItem("access_token");
            const response = await fetch(`http://localhost:8000/documents/${documentId}/eli5`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });
            
            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                throw new Error(body.detail || response.statusText);
            }
            
            const updatedSummary = await response.json();
            setData(updatedSummary);
            setTab("eli5");
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : "Failed to generate ELI5 summary");
        } finally {
            setGeneratingEli5(false);
        }
    };

    if (error) {
        return (
            <Alert variant="destructive">
                <p className="text-sm">Error fetching summary: {error}</p>
            </Alert>
        );
    }
    if (!data) {
        return <p className="text-center py-10">Loading summary…</p>;
    }

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between">
                    <div>
                        <CardTitle>Research Paper Summary</CardTitle>
                        <CardDescription className="mt-1 text-xs text-muted-foreground">
                            Document ID: {data.document_id}
                        </CardDescription>
                    </div>
                    <Download
                        className="h-5 w-5 cursor-pointer"
                        onClick={() => {
                            // export logic (optional)
                        }}
                    />
                </div>
            </CardHeader>

            <CardContent>
                <Tabs value={tab} onValueChange={(v) => setTab(v as any)}>
                    <TabsList className="grid grid-cols-5">
                        <TabsTrigger value="introduction">Introduction</TabsTrigger>
                        <TabsTrigger value="methods">Methods</TabsTrigger>
                        <TabsTrigger value="results">Results</TabsTrigger>
                        <TabsTrigger value="conclusion">Conclusion</TabsTrigger>
                        <TabsTrigger value="eli5" className="flex items-center gap-2">
                            <Baby className="h-4 w-4" />
                            ELI5
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="introduction" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Research Introduction</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.introduction}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="methods" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Research Methods</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.methods}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="results" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Research Results</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.results}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="conclusion" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Research Conclusion</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.conclusion}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="eli5" className="mt-4 space-y-6">
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <h4 className="flex items-center space-x-2">
                                    <Baby className="h-4 w-4" />
                                    <span>Explain Like I'm 5</span>
                                </h4>
                                {!data.eli5_summary && (
                                    <Button 
                                        onClick={generateEli5} 
                                        disabled={generatingEli5}
                                        size="sm"
                                        className="flex items-center gap-2"
                                    >
                                        <Sparkles className="h-4 w-4" />
                                        {generatingEli5 ? "Generating..." : "Generate ELI5"}
                                    </Button>
                                )}
                            </div>
                            {data.eli5_summary ? (
                                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border-l-4 border-blue-400">
                                    <p className="text-sm text-gray-800 leading-relaxed">{data.eli5_summary}</p>
                                </div>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    <Baby className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                    <p className="text-sm">Click the button above to generate a simple explanation that a 5-year-old could understand!</p>
                                </div>
                            )}
                        </div>
                    </TabsContent>
                </Tabs>
                {/* Recommendations Section */}
                <div className="mt-10">
                    <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                        <Quote className="h-5 w-5 text-blue-500" />
                        Recommended Research Papers
                    </h3>
                    {recLoading && <p>Loading recommendations…</p>}
                    {recError && <Alert variant="destructive"><p className="text-sm">{recError}</p></Alert>}
                    {recommendations && recommendations.length === 0 && !recLoading && (
                        <p className="text-muted-foreground text-sm">No recommendations found for this document.</p>
                    )}
                    {recommendations && recommendations.length > 0 && (
                        <ul className="space-y-4 mt-2">
                            {recommendations.map((paper, idx) => (
                                <li key={idx} className="border rounded-lg p-4 bg-gray-50">
                                    <a href={paper.url} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-700 hover:underline">
                                        {paper.title}
                                    </a>
                                    <div className="text-xs text-muted-foreground mt-1">{paper.authors} {paper.year && `· ${paper.year}`}</div>
                                    {paper.abstract && <p className="text-sm mt-2 line-clamp-4">{paper.abstract}</p>}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
