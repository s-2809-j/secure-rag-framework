package com.sentinel.chat.service;

import com.sentinel.auth.model.User;
import com.sentinel.chat.dto.ChatRequest;
import com.sentinel.chat.dto.ChatResponse;
import com.sentinel.fastapi.client.FastApiClient;
import com.sentinel.fastapi.dto.FastApiChatRequest;
import com.sentinel.fastapi.dto.FastApiChatResponse;
import com.sentinel.fastapi.exception.FastApiException;
import com.sentinel.session.model.ChatMessage;
import com.sentinel.session.model.ChatSession;
import com.sentinel.session.service.ChatSessionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    private final FastApiClient      fastApiClient;
    private final ChatSessionService chatSessionService;

    @Transactional
    public ChatResponse processChat(ChatRequest request) {
        String requestId = UUID.randomUUID().toString();
        User   user      = getCurrentUser();

        if (request.query() == null || request.query().isBlank()) {
            throw new com.sentinel.exception.SentinelException("INVALID_REQUEST", "Query cannot be empty.");
        }
        if (request.query().length() > 4000) {
            throw new com.sentinel.exception.SentinelException("INVALID_REQUEST", "Query exceeds maximum allowed length.");
        }

        log.debug("Processing chat request [{}] for user: {}", requestId, user.getUsername());

        // Resolve or create session
        ChatSession session = resolveSession(request, user);

        // Persist user message
        chatSessionService.addMessage(session, "user", request.query(), requestId);

        // Delegate to FastAPI AI Engine
        FastApiChatRequest fastApiRequest = FastApiChatRequest.of(
                request.query(),
                requestId,
                user.getId().toString(),
                session.getId().toString()
        );

        FastApiChatResponse fastApiResponse;

        try {
            fastApiResponse = fastApiClient.chat(fastApiRequest);
        } catch (FastApiException ex) {
            log.error("FastAPI chat failed for request [{}]: {}", requestId, ex.getMessage());
            throw ex;
        }
        log.debug("FastAPI raw response — success={} message={} responseText={} blocked={} riskScore={}",
                fastApiResponse.success(),
                fastApiResponse.message(),
                fastApiResponse.responseText(),
                fastApiResponse.blocked(),
                fastApiResponse.riskScore());
        // Persist assistant response using responseText (the actual AI answer),
        // not message (which is a status string e.g. "Response generated successfully.")
        String aiAnswer = fastApiResponse.responseText();

        if (fastApiResponse.success() && aiAnswer != null) {
            chatSessionService.addMessage(
                    session, "assistant", aiAnswer, requestId
            );
        }

        log.debug("Chat request [{}] completed — success={} blocked={}",
                requestId, fastApiResponse.success(), fastApiResponse.blocked());

        return ChatResponse.of(
                requestId,
                fastApiResponse.success(),
                fastApiResponse.message(),
                aiAnswer,                       // ← was fastApiResponse.data(), now the actual answer
                session.getId().toString()
        );
    }

    // ── Internal ──────────────────────────────────────────────────────────

    private ChatSession resolveSession(ChatRequest request, User user) {
        if (request.sessionId() != null && !request.sessionId().isBlank()) {
            try {
                Long sessionId = Long.parseLong(request.sessionId());
                return chatSessionService.getSessionForUser(sessionId, user.getId());
            } catch (NumberFormatException ex) {
                log.warn("sessionId '{}' is not a numeric ID — creating new session", request.sessionId());
            } catch (com.sentinel.exception.ResourceNotFoundException ex) {
                log.warn("Session {} not found for user {} — creating new session",
                        request.sessionId(), user.getUsername());
            }
        }
        return chatSessionService.createSession(
                user, "Chat " + UUID.randomUUID().toString().substring(0, 8)
        );
    }
    private User getCurrentUser() {
        return (User) SecurityContextHolder.getContext()
                .getAuthentication()
                .getPrincipal();
    }
}