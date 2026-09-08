package com.sentinel.fastapi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;

@Builder
public record FastApiChatRequest(

        @JsonProperty("request_id")
        String requestId,

        @JsonProperty("query")
        String query,

        @JsonProperty("user_id")
        String userId,

        @JsonProperty("session_id")
        String sessionId

) {

    public static FastApiChatRequest of(
            String query,
            String requestId,
            String userId,
            String sessionId
    ) {
        return FastApiChatRequest.builder()
                .requestId(requestId)
                .query(query)
                .userId(userId)
                .sessionId(sessionId)
                .build();
    }
}