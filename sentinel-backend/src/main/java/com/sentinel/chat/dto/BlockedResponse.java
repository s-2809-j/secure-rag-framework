package com.sentinel.chat.dto;

import lombok.Builder;

import java.time.Instant;

@Builder
public record BlockedResponse(
        String  requestId,
        String  reason,
        Instant timestamp
) {
    public static BlockedResponse of(String requestId, String reason) {
        return BlockedResponse.builder()
                .requestId(requestId)
                .reason(reason)
                .timestamp(Instant.now())
                .build();
    }
}