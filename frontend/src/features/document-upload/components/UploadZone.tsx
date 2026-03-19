"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, File, Loader2 } from "lucide-react";
import { useTranslation } from "@/hooks/use-translation";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface UploadZoneProps {
  onUploadSuccess: (file: File) => void;
  isUploading?: boolean;
}

export function UploadZone({
  onUploadSuccess,
  isUploading = false,
}: UploadZoneProps) {
  const { t } = useTranslation();
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    const validExtensions = [".pdf", ".mp4"];
    const isExtensionValid = validExtensions.some((ext) =>
      file.name.toLowerCase().endsWith(ext),
    );
    const isSizeValid = file.size <= 50 * 1024 * 1024; // 50MB limit

    if (!isExtensionValid) {
      toast.error("Invalid file type. Please upload PDF or MP4.");
      return;
    }

    if (!isSizeValid) {
      toast.error("File is too large. Maximum allowed size is 50MB.");
      return;
    }

    setSelectedFile(file);
  };

  const handleUploadSubmit = () => {
    if (selectedFile) {
      onUploadSuccess(selectedFile);
      // Reset after submission logic is handed over
      setSelectedFile(null);
    }
  };

  return (
    <div className="w-full">
      <div
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 md:p-12 transition-all flex flex-col items-center justify-center text-center cursor-pointer overflow-hidden",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-secondary/50",
          (selectedFile || isUploading) && "pointer-events-none", // Disable drop zone if file selected or uploading
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() =>
          !selectedFile && !isUploading && fileInputRef.current?.click()
        }
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".pdf,.mp4"
          onChange={handleFileChange}
        />

        {isUploading ? (
          <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
            <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
            <p className="text-lg font-medium text-foreground">
              {t.documents.uploading}
            </p>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
            <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mb-4">
              <File className="w-8 h-8" />
            </div>
            <p className="text-lg font-medium text-foreground max-w-75 truncate">
              {selectedFile.name}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 bg-secondary text-muted-foreground rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-foreground">
              {t.documents.uploadBoxTitle}
            </h3>
            <p className="text-sm text-muted-foreground mt-2 max-w-md">
              {t.documents.uploadBoxSubtitle}
            </p>
          </>
        )}
      </div>

      {/* Action Area below the dropzone when a file is selected */}
      {selectedFile && !isUploading && (
        <div className="mt-4 flex items-center justify-end gap-3 animate-in slide-in-from-top-2">
          <Button variant="outline" onClick={() => setSelectedFile(null)}>
            Cancel
          </Button>
          <Button onClick={handleUploadSubmit} className="gap-2">
            <UploadCloud className="w-4 h-4" />
            Start Processing
          </Button>
        </div>
      )}
    </div>
  );
}
