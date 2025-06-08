"use client"

import { DashboardHeader } from "@/app/components/dashboard-header"
import { FileUploadSection } from "@/app/components/file-upload"
import { CurrentSummarySection } from "@/app/components/current-summary-section"
import { PreviousSummariesSection } from "@/app/components/previous-summaries"
import { useState } from "react";

export default function DashboardPage() {
    const [currentDocId, setCurrentDocId] = useState<number | null>(null);
    return (
        <div className="min-h-screen bg-background">
            <DashboardHeader />
            <main className="container py-8">
                <div className="grid gap-8 lg:grid-cols-3">
                    {/* Left Column - Upload and Current Summary */}
                    <div className="lg:col-span-2 space-y-8">
                        <FileUploadSection onUploadComplete={setCurrentDocId} />
                        {currentDocId ? (
                            <CurrentSummarySection documentId={currentDocId} />
                        ) : (
                            <p className="text-center text-sm text-muted-foreground">
                                Upload a paper to see its AI summary here.
                            </p>
                        )}
                    </div>

                    {/* Right Column - Previous Summaries */}
                    <div className="lg:col-span-1">
                        <PreviousSummariesSection />
                    </div>
                </div>
            </main>
        </div>
    )
}
