package com.sentinel.chat.controller;

import com.sentinel.chat.dto.ChatRequest;
import com.sentinel.chat.dto.ChatResponse;
import com.sentinel.chat.service.ChatService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<ChatResponse> chat(
            @Valid @RequestBody ChatRequest request) {
        return ResponseEntity.ok(chatService.processChat(request));
    }
}