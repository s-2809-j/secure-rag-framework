package com.sentinel.fastapi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;

@Builder
public record FastApiDocumentRequest(

        @JsonProperty("request_id")
        String requestId,

        @JsonProperty("file_path")
        String filePath,

        @JsonProperty("filename")
        String filename,

        @JsonProperty("extension")
        String extension,

        @JsonProperty("mime_type")
        String mimeType,

        @JsonProperty("size_bytes")
        long sizeBytes,

        @JsonProperty("checksum")
        String checksum,

        @JsonProperty("user_id")
        String userId

) {
}