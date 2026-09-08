package com.sentinel.document.dto;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.sentinel.fastapi.dto.FastApiDocumentResponse.IngestionResult;
import lombok.Builder;
import lombok.extern.jackson.Jacksonized;

import java.time.Instant;

@Builder
@Jacksonized
@JsonInclude(JsonInclude.Include.NON_NULL)
public record KnowledgeUploadResponse(
        @JsonProperty("requestId")    String requestId,
        @JsonProperty("success")      boolean success,
        @JsonProperty("message")      String message,
        @JsonProperty("data")         KnowledgeUploadData data,
        @JsonProperty("timestamp")    Instant timestamp
) {

    private static final ObjectMapper INGESTION_MAPPER = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Builder
    @Jacksonized
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record KnowledgeUploadData(
            @JsonProperty("status")           String status,
            @JsonProperty("documentId")       String documentId,
            @JsonProperty("chunkCount")       Integer chunkCount,
            @JsonProperty("embeddingCount")   Integer embeddingCount,
            @JsonProperty("ingestionMessage") String ingestionMessage
    ) {}

    public static KnowledgeUploadResponse of(
            String requestId,
            boolean success,
            String message,
            Object ingestionResultRaw) {

        KnowledgeUploadData data = null;
        IngestionResult ingestionResult = toIngestionResult(ingestionResultRaw);

        if (ingestionResult != null) {
            data = KnowledgeUploadData.builder()
                    .status(ingestionResult.status())
                    .documentId(ingestionResult.documentId())
                    .chunkCount(ingestionResult.chunkCount())
                    .embeddingCount(ingestionResult.embeddingCount())
                    .ingestionMessage(ingestionResult.message())
                    .build();
        }

        return KnowledgeUploadResponse.builder()
                .requestId(requestId)
                .success(success)
                .message(message)
                .data(data)
                .timestamp(Instant.now())
                .build();
    }

    static IngestionResult toIngestionResult(Object raw) {
        if (raw == null) {
            return null;
        }
        if (raw instanceof IngestionResult typed) {
            return typed;
        }
        return INGESTION_MAPPER.convertValue(raw, IngestionResult.class);
    }
}
