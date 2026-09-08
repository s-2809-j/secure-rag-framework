package com.sentinel.fastapi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Shared Feign response DTO for document analyze and knowledge upload.
 * Field names must match FastAPI {@code DocumentApiResponse} /
 * {@code KnowledgeApiResponse} JSON exactly.
 */
public record FastApiDocumentResponse(

        @JsonProperty("request_id")
        String requestId,

        @JsonProperty("success")
        boolean success,

        @JsonProperty("message")
        String message,

        @JsonProperty("analysis_result")
        Object analysisResult,

        /**
         * Kept as {@link Object} (same pattern as {@code analysis_result})
         * so Jackson always retains the FastAPI payload even when nested
         * shape differs slightly. Mapped to {@link IngestionResult} in
         * {@code KnowledgeUploadResponse}.
         */
        @JsonProperty("ingestion_result")
        Object ingestionResult,

        @JsonProperty("workflow")
        String workflow

) {
    public record IngestionResult(

            @JsonProperty("status")
            String status,

            @JsonProperty("success")
            boolean success,

            @JsonProperty("document_id")
            String documentId,

            @JsonProperty("chunk_count")
            Integer chunkCount,

            @JsonProperty("embedding_count")
            Integer embeddingCount,

            @JsonProperty("message")
            String message
    ) {}
}
