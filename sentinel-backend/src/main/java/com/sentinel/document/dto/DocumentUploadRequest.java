package com.sentinel.document.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record DocumentUploadRequest(

        @NotBlank(message = "File path is required")
        String filePath,

        @NotBlank(message = "Filename is required")
        String filename,

        @NotBlank(message = "Extension is required")
        String extension,

        @NotBlank(message = "MIME type is required")
        String mimeType,

        @NotNull(message = "File size is required")
        @Positive(message = "File size must be positive")
        Long sizeBytes

) {}