package com.sentinel.chat.dto;

import lombok.Builder;

import java.time.Instant;

@Builder
public record ChatResponse(
        String  requestId,
        boolean success,
        String  message,
        Object  data,
        String  sessionId,
        Instant timestamp
) {
    public static ChatResponse of(String requestId, boolean success,
                                  String message, Object data, String sessionId) {
        return ChatResponse.builder()
                .requestId(requestId)
                .success(success)
                .message(message)
                .data(data)
                .sessionId(sessionId)
                .timestamp(Instant.now())
                .build();
    }
}