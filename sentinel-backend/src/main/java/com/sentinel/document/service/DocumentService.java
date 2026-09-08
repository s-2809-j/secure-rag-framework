package com.sentinel.document.service;

import com.sentinel.document.dto.DocumentAnalysisResponse;
import com.sentinel.document.dto.DocumentUploadRequest;
import com.sentinel.document.dto.KnowledgeUploadResponse;
import com.sentinel.fastapi.client.FastApiClient;
import com.sentinel.fastapi.dto.FastApiDocumentRequest;
import com.sentinel.fastapi.dto.FastApiDocumentResponse;
import com.sentinel.fastapi.exception.FastApiException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class DocumentService {

    private final FastApiClient fastApiClient;

    // ── Analyze ───────────────────────────────────────────────────────────

    public DocumentAnalysisResponse analyzeDocument(DocumentUploadRequest request, String userId) {
        String requestId = UUID.randomUUID().toString();
        log.debug("Analyzing document [{}]: {}", requestId, request.filename());
        FastApiDocumentRequest fastApiRequest = buildFastApiRequest(request, requestId, userId);

        FastApiDocumentResponse fastApiResponse;
        try {
            fastApiResponse = fastApiClient.analyzeDocument(fastApiRequest);
            log.info(
                    "FastAPI Analyze Response -> success={} message={} data={}",
                    fastApiResponse.success(),
                    fastApiResponse.message(),
                    fastApiResponse.analysisResult()
            );
        } catch (FastApiException ex) {
            log.error("FastAPI document analysis failed [{}]: {}", requestId, ex.getMessage());
            throw ex;
        }

        log.debug("Document analysis [{}] completed — success={}", requestId, fastApiResponse.success());

        return DocumentAnalysisResponse.of(
                requestId,
                fastApiResponse.success(),
                fastApiResponse.message(),
                fastApiResponse.analysisResult()
        );
    }

    // ── Upload to Knowledge Base ──────────────────────────────────────────

    public KnowledgeUploadResponse uploadToKnowledge(DocumentUploadRequest request, String userId) {
        String requestId = UUID.randomUUID().toString();
        log.debug("Uploading document to knowledge base [{}]: {}", requestId, request.filename());
        FastApiDocumentRequest fastApiRequest = buildFastApiRequest(request, requestId, userId);

        FastApiDocumentResponse fastApiResponse;
        try {
            fastApiResponse = fastApiClient.uploadDocument(fastApiRequest);
            log.info(
                    "FastAPI Upload Response -> success={} message={} ingestion_result={}",
                    fastApiResponse.success(),
                    fastApiResponse.message(),
                    fastApiResponse.ingestionResult()
            );
        } catch (FastApiException ex) {
            log.error("FastAPI knowledge upload failed [{}]: {}", requestId, ex.getMessage());
            throw ex;
        }

        log.debug("Knowledge upload [{}] completed — success={}", requestId, fastApiResponse.success());

        return KnowledgeUploadResponse.of(
                requestId,
                fastApiResponse.success(),
                fastApiResponse.message(),
                fastApiResponse.ingestionResult()
        );
    }

    // ── Internal ──────────────────────────────────────────────────────────

    private FastApiDocumentRequest buildFastApiRequest(DocumentUploadRequest request,
                                                       String requestId,
                                                       String userId) {

        return FastApiDocumentRequest.builder()
                .requestId(requestId)
                .filePath(request.filePath())
                .filename(request.filename())
                .extension(request.extension())
                .mimeType(request.mimeType())
                .sizeBytes(request.sizeBytes() != null ? request.sizeBytes() : 0L)
                .checksum(null)
                .userId(userId)
                .build();
    }
}