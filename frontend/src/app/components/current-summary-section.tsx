"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Copy, Download, Share, BookOpen, Quote, Users } from "lucide-react"
import { Alert } from "@/components/ui/alert"

interface SummaryRead {
    id: number;
    document_id: number;
    introduction: string;
    methods: string;
    results: string;
    conclusion: string;
}

export function CurrentSummarySection({ documentId }: { documentId: number }) {
    const [data, setData] = useState<SummaryRead | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<"summary" | "references" | "citations">("summary");

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
                        <CardTitle>Summary ID: {data.id}</CardTitle>
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
                    <TabsList className="grid grid-cols-4">
                        <TabsTrigger value="introduction">Introduction</TabsTrigger>
                        <TabsTrigger value="methods">Methods</TabsTrigger>
                        <TabsTrigger value="results">Results</TabsTrigger>
                        <TabsTrigger value="conclusion">Conclusion</TabsTrigger>
                    </TabsList>

                    <TabsContent value="introduction" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Introduction</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.introduction}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="methods" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Methods</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.methods}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="results" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Results</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.results}</p>
                        </div>
                    </TabsContent>

                    <TabsContent value="conclusion" className="mt-4 space-y-6">
                        <div>
                            <h4 className="flex items-center space-x-2">
                                <BookOpen className="h-4 w-4" />
                                <span>Conclusion</span>
                            </h4>
                            <p className="text-sm text-muted-foreground">{data.conclusion}</p>
                        </div>
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    )
}
