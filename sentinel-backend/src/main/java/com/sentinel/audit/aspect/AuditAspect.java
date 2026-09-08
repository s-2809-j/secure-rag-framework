package com.sentinel.audit.aspect;

import com.sentinel.audit.service.AuditService;
import com.sentinel.auth.model.User;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.UUID;

@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class AuditAspect {

    private final AuditService auditService;

    @Pointcut("within(@org.springframework.web.bind.annotation.RestController *)")
    public void restControllerMethods() {}

    @Around("restControllerMethods()")
    public Object auditControllerCall(ProceedingJoinPoint joinPoint) throws Throwable {
        HttpServletRequest request = getCurrentRequest();
        String endpoint   = request != null ? request.getRequestURI()  : "unknown";
        String method     = request != null ? request.getMethod()       : "unknown";
        String ipAddress  = extractIp(request);
        String requestId  = request != null ? request.getHeader("X-Request-ID") : null;
        String action     = method + " " + endpoint;

        UUID   userId     = extractUserId();
        Object result     = null;
        int    statusCode = 200;

        try {
            result = joinPoint.proceed();
            if (result instanceof ResponseEntity<?> re) {
                statusCode = re.getStatusCode().value();
            }
            return result;
        } catch (Throwable ex) {
            statusCode = 500;
            throw ex;
        } finally {
            auditService.log(userId, action, endpoint, requestId, ipAddress, statusCode, null);
        }
    }

    // ── Internal helpers ──────────────────────────────────────────────────

    private UUID extractUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof User user) {
            return user.getId();
        }
        return null;
    }

    private String extractIp(HttpServletRequest request) {
        if (request == null) return null;
        String forwarded = request.getHeader("X-Forwarded-For");
        if (forwarded != null && !forwarded.isBlank()) {
            return forwarded.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }

    private HttpServletRequest getCurrentRequest() {
        try {
            ServletRequestAttributes attrs =
                    (ServletRequestAttributes) RequestContextHolder.currentRequestAttributes();
            return attrs.getRequest();
        } catch (Exception ex) {
            return null;
        }
    }
}