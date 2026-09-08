package com.sentinel.session.repository;

import com.sentinel.session.model.ChatSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ChatSessionRepository extends JpaRepository<ChatSession, Long> {

    List<ChatSession> findByUserIdOrderByUpdatedAtDesc(UUID userId);

    Optional<ChatSession> findByIdAndUserId(Long id, UUID userId);
}