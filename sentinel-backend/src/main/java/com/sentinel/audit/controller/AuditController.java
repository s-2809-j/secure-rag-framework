package com.sentinel.audit.controller;

import com.sentinel.audit.model.AuditLog;
import com.sentinel.audit.service.AuditService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/audit")
@RequiredArgsConstructor
public class AuditController {

    private final AuditService auditService;

    @GetMapping("/logs")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Page<AuditLog>> getLogs(
            @PageableDefault(size = 50, sort = "timestamp") Pageable pageable) {
        return ResponseEntity.ok(auditService.getAllLogs(pageable));
    }

    @GetMapping("/logs/user/{userId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Page<AuditLog>> getLogsByUser(
            @PathVariable UUID userId,
            @PageableDefault(size = 50) Pageable pageable) {
        return ResponseEntity.ok(auditService.getLogsByUser(userId, pageable));
    }

    @GetMapping("/logs/range")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Page<AuditLog>> getLogsByRange(
            @RequestParam Instant from,
            @RequestParam Instant to,
            @PageableDefault(size = 50) Pageable pageable) {
        return ResponseEntity.ok(auditService.getLogsByTimeRange(from, to, pageable));
    }
}