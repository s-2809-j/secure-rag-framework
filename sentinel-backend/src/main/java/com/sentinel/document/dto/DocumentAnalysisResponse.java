package com.sentinel.document.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.extern.jackson.Jacksonized;

import java.time.Instant;

@Builder
@Jacksonized
@JsonInclude(JsonInclude.Include.NON_NULL)
public record DocumentAnalysisResponse(
        String requestId,
        boolean success,
        String message,
        Object data,          // raw analysis_result from FastAPI
        Instant timestamp
) {

    public static DocumentAnalysisResponse of(
            String requestId,
            boolean success,
            String message,
            Object analysisResult) {

        return DocumentAnalysisResponse.builder()
                .requestId(requestId)
                .success(success)
                .message(message)
                .data(analysisResult)
                .timestamp(Instant.now())
                .build();
    }
}