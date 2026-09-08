package com.sentinel.fastapi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record FastApiChatResponse(
        @JsonProperty("success")       boolean success,
        @JsonProperty("workflow")      String  workflow,
        @JsonProperty("request_id")    String  requestId,
        @JsonProperty("message")       String  message,
        @JsonProperty("response_text") String  responseText,
        @JsonProperty("blocked")       boolean blocked,
        @JsonProperty("risk_score")    Double  riskScore
) {}