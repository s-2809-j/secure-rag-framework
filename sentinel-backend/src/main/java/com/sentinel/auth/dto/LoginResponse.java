package com.sentinel.auth.dto;

import lombok.Builder;

@Builder
public record LoginResponse(
        String accessToken,
        String refreshToken,
        String tokenType,
        long   expiresIn,
        String username,
        String role
) {
    public static LoginResponse of(String accessToken, String refreshToken,
                                   long expiresIn, String username, String role) {
        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(expiresIn)
                .username(username)
                .role(role)
                .build();
    }
}