package com.sentinel.audit.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "audit_logs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private UUID userId;

    @Column(nullable = false, length = 100)
    private String action;

    @Column(nullable = false, length = 200)
    private String endpoint;

    @Column(name = "request_id", length = 100)
    private String requestId;

    @Column(name = "ip_address", length = 45)
    private String ipAddress;

    @Column(name = "status_code")
    private Integer statusCode;

    @Column(nullable = false)
    private Instant timestamp;

    @Column(columnDefinition = "TEXT")
    private String details;

    @PrePersist
    protected void onCreate() {
        this.timestamp = Instant.now();
    }
}