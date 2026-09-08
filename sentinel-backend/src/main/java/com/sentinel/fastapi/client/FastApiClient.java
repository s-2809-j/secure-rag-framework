package com.sentinel.fastapi.client;

import com.sentinel.config.FastApiClientConfig;
import com.sentinel.fastapi.dto.FastApiChatRequest;
import com.sentinel.fastapi.dto.FastApiChatResponse;
import com.sentinel.fastapi.dto.FastApiDocumentRequest;
import com.sentinel.fastapi.dto.FastApiDocumentResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

@FeignClient(
        name = "fastapi-client",
        url = "${fastapi.base-url}",
        configuration = FastApiClientConfig.class   // ← THIS is the fix
)
public interface FastApiClient {

    @PostMapping("/v1/chat")
    FastApiChatResponse chat(@RequestBody FastApiChatRequest request);

    @PostMapping("/v1/documents/analyze")
    FastApiDocumentResponse analyzeDocument(@RequestBody FastApiDocumentRequest request);

    @PostMapping("/v1/documents/upload")
    FastApiDocumentResponse uploadDocument(@RequestBody FastApiDocumentRequest request);
}