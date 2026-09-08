package com.sentinel.session.service;

import com.sentinel.auth.model.User;
import com.sentinel.exception.ResourceNotFoundException;
import com.sentinel.session.model.ChatMessage;
import com.sentinel.session.model.ChatSession;
import com.sentinel.session.repository.ChatSessionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatSessionService {

    private final ChatSessionRepository chatSessionRepository;

    @Transactional
    public ChatSession createSession(User user, String sessionName) {
        ChatSession session = ChatSession.builder()
                .user(user)
                .sessionName(sessionName)
                .build();
        ChatSession saved = chatSessionRepository.save(session);
        log.debug("Created chat session [{}] for user: {}", saved.getId(), user.getUsername());
        return saved;
    }

    @Transactional(readOnly = true)
    public ChatSession getSessionForUser(Long sessionId, UUID userId) {
        return chatSessionRepository.findByIdAndUserId(sessionId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("ChatSession", sessionId));
    }

    @Transactional(readOnly = true)
    public List<ChatSession> getSessionsForUser(UUID userId) {
        return chatSessionRepository.findByUserIdOrderByUpdatedAtDesc(userId);
    }

    @Transactional
    public void addMessage(ChatSession session, String role,
                           String content, String requestId) {
        ChatMessage message = ChatMessage.builder()
                .session(session)
                .role(role)
                .content(content)
                .requestId(requestId)
                .build();
        session.getMessages().add(message);
        chatSessionRepository.save(session);
    }
}