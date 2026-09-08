package com.sentinel.chat.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ChatRequest(

        @NotBlank(message = "Query must not be blank")
        @Size(max = 4000, message = "Query must not exceed 4000 characters")
        String query,

        String sessionId
) {}