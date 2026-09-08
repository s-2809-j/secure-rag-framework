package com.sentinel.fastapi.dto;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.module.paramnames.ParameterNamesModule;
import com.sentinel.document.dto.KnowledgeUploadResponse;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class FastApiDocumentResponseDeserializationTest {

    @Test
    void deserializesIngestionResultFromFastApiPayload() throws Exception {
        String json = """
                {
                  "request_id": "upload-probe-001",
                  "success": true,
                  "message": "Document ingested into knowledge base successfully.",
                  "ingestion_result": {
                    "status": "SUCCESS",
                    "success": true,
                    "document_id": null,
                    "chunk_count": 3,
                    "embedding_count": 3,
                    "message": "Document successfully ingested."
                  },
                  "workflow": "knowledge_upload"
                }
                """;

        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new ParameterNamesModule())
                .registerModule(new JavaTimeModule())
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        FastApiDocumentResponse response = mapper.readValue(json, FastApiDocumentResponse.class);

        assertThat(response.success()).isTrue();
        assertThat(response.ingestionResult()).isInstanceOf(Map.class);

        KnowledgeUploadResponse mapped = KnowledgeUploadResponse.of(
                response.requestId(),
                response.success(),
                response.message(),
                response.ingestionResult()
        );

        assertThat(mapped.data()).isNotNull();
        assertThat(mapped.data().status()).isEqualTo("SUCCESS");
        assertThat(mapped.data().chunkCount()).isEqualTo(3);
        assertThat(mapped.data().embeddingCount()).isEqualTo(3);
        assertThat(mapped.data().ingestionMessage())
                .isEqualTo("Document successfully ingested.");
    }
}
