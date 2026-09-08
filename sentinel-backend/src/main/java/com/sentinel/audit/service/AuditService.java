package com.sentinel.audit.service;

import com.sentinel.audit.model.AuditLog;
import com.sentinel.audit.repository.AuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    @Async
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void log(UUID userId, String action, String endpoint,
                    String requestId, String ipAddress, Integer statusCode,
                    String details) {
        try {
            AuditLog entry = AuditLog.builder()
                    .userId(userId)
                    .action(action)
                    .endpoint(endpoint)
                    .requestId(requestId)
                    .ipAddress(ipAddress)
                    .statusCode(statusCode)
                    .details(details)
                    .build();
            auditLogRepository.save(entry);
        } catch (Exception ex) {
            // Audit must never break the main request flow
            log.error("Failed to persist audit log for action [{}] endpoint [{}]: {}",
                    action, endpoint, ex.getMessage());
        }
    }

    @Transactional(readOnly = true)
    public Page<AuditLog> getAllLogs(Pageable pageable) {
        return auditLogRepository.findAllByOrderByTimestampDesc(pageable);
    }

    @Transactional(readOnly = true)
    public Page<AuditLog> getLogsByUser(UUID userId, Pageable pageable) {
        return auditLogRepository.findByUserId(userId, pageable);
    }

    @Transactional(readOnly = true)
    public Page<AuditLog> getLogsByTimeRange(Instant from, Instant to, Pageable pageable) {
        return auditLogRepository.findByTimestampBetween(from, to, pageable);
    }
}