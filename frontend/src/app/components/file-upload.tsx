"use client"

import React, { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, FileText, X, CheckCircle, AlertCircle } from "lucide-react"

interface UploadedFile {
    id: string
    name: string
    size: number
    status: "uploading" | "processing" | "completed" | "error"
    progress: number
    error?: string
}

interface FileUploadSectionProps {
  onUploadComplete: (docId: number) => void;
}

export function FileUploadSection({ onUploadComplete }: FileUploadSectionProps) {
    const [files, setFiles] = useState<UploadedFile[]>([])
    const [isDragOver, setIsDragOver] = useState(false)

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(true)
    }, [])

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
    }, [])

    const uploadFileToServer = useCallback(async (file: File, tempId: string) => {
        const formData = new FormData()
        formData.append("file", file)
    
        const token = localStorage.getItem("access_token")
    
        try {
            const resp = await fetch("https://research-cite.onrender.com/documents", {
                method: "POST",
                body: formData,
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            })
            if (!resp.ok) throw new Error(resp.statusText)
            const document = await resp.json()
            onUploadComplete(document.id)
            setFiles((prev) =>
                prev.map((f) =>
                    f.id === tempId
                        ? {
                            ...f,
                            id: document.id.toString(),
                            status: document.status.toLowerCase() as UploadedFile["status"],
                            progress: document.progress,
                        }
                        : f
                )
            )
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : "Unknown error"
            console.error(err)
            setFiles((prev) =>
                prev.map((f) =>
                    f.id === tempId
                        ? { ...f, status: "error", progress: 0, error: errorMessage }
                        : f
                )
            )
        }
    }, [onUploadComplete])
    

    const handleFiles = useCallback((fileList: File[]) => {
        const pdfs = fileList.filter((f) => f.type === "application/pdf")
        if (pdfs.length !== fileList.length) {
            console.warn("Some files were ignored: only PDFs allowed.")
        }

        pdfs.forEach((file) => {
            const tempId = crypto.randomUUID()
            const newFile: UploadedFile = {
                id: tempId,
                name: file.name,
                size: file.size,
                status: "uploading",
                progress: 0,
            }
            setFiles((prev) => [...prev, newFile])
            uploadFileToServer(file, tempId)
        })
    }, [uploadFileToServer])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
        const dropped = Array.from(e.dataTransfer.files)
        handleFiles(dropped)
    }, [handleFiles])

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files) return
        handleFiles(Array.from(e.target.files))
    }, [handleFiles])



    const removeFile = useCallback((id: string) => {
        setFiles((prev) => prev.filter((f) => f.id !== id))
    }, [])

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return "0 Bytes"
        const k = 1024
        const sizes = ["Bytes", "KB", "MB", "GB"]
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Upload Research Papers</CardTitle>
                <CardDescription>
                    Upload PDF files of research papers, academic articles, or scholarly documents to get AI-powered summaries and references
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`relative  border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
            ${isDragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"}`}
                >
                    <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <div className="space-y-2">
                        <p className="text-lg font-medium">Drop your research papers here</p>
                        <p className="text-sm text-muted-foreground">or click to browse</p>
                    </div>
                    <input
                        type="file"
                        multiple
                        accept=".pdf"
                        onChange={handleFileSelect}
                        className="absolute inset-0 w-full h-full opacity-0"
                    />
                    <Button variant="outline" className="mt-4">
                        Choose Files
                    </Button>
                </div>

                {files.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="font-medium">Processing Files</h4>

                        {files.map((file) => (
                            <div key={file.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                                <FileText className="h-8 w-8 text-primary flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <p className="text-sm font-medium truncate">{file.name}</p>
                                        <div className="flex items-center space-x-2">
                                            {file.status === "completed" && <CheckCircle className="h-4 w-4 text-green-500" />}
                                            {file.status === "error" && <AlertCircle className="h-4 w-4 text-red-500" />}
                                            <Button variant="ghost" size="sm" onClick={() => removeFile(file.id)} className="h-6 w-6 p-0">
                                                <X className="h-3 w-3" />
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
                                        <span>{formatFileSize(file.size)}</span>
                                        <span className="capitalize">
                                            {{
                                                uploading: "Uploading...",
                                                processing: "Processing...",
                                                completed: "Completed",
                                                error: "Error",
                                            }[file.status]}
                                        </span>
                                    </div>

                                    {(file.status === "uploading" || file.status === "processing") && (
                                        <Progress value={file.progress} className="h-2" />
                                    )}

                                    {file.error && (
                                        <Alert variant="destructive" className="mt-2">
                                            <AlertDescription className="text-xs">{file.error}</AlertDescription>
                                        </Alert>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
