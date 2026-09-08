package com.sentinel.auth.service;

import com.sentinel.auth.model.User;
import com.sentinel.config.JwtConfig;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class JwtService {

    private final JwtConfig jwtConfig;

    // ── Token generation ─────────────────────────────────────────────────

    public String generateAccessToken(User user) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("role", user.getRole().name());
        claims.put("email", user.getEmail());
        claims.put("type", "access");
        return buildToken(claims, user.getUsername(), jwtConfig.getAccessExpiryMs());
    }

    public String generateRefreshToken(User user) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("type", "refresh");
        return buildToken(claims, user.getUsername(), jwtConfig.getRefreshExpiryMs());
    }

    // ── Token validation ─────────────────────────────────────────────────

    public boolean isTokenValid(String token) {
        try {
            Claims claims = extractAllClaims(token);
            return !claims.getExpiration().before(new Date());
        } catch (JwtException | IllegalArgumentException ex) {
            log.debug("JWT validation failed: {}", ex.getMessage());
            return false;
        }
    }

    // Add after isTokenValid(String token) method

    public boolean isTokenValid(String token, org.springframework.security.core.userdetails.UserDetails userDetails) {
        try {
            final String username = extractUsername(token);
            return username.equals(userDetails.getUsername())
                    && userDetails.isEnabled()
                    && isTokenValid(token);
        } catch (JwtException | IllegalArgumentException ex) {
            return false;
        }
    }
    public boolean isAccessToken(String token) {
        try {
            return "access".equals(extractAllClaims(token).get("type", String.class));
        } catch (JwtException ex) {
            return false;
        }
    }
    // Add after isAccessToken() method

    public boolean isRefreshToken(String token) {
        try {
            return "refresh".equals(extractAllClaims(token).get("type", String.class));
        } catch (JwtException ex) {
            return false;
        }
    }

    public long getAccessExpiryMs() {
        return jwtConfig.getAccessExpiryMs();
    }

    public long getRefreshExpiryMs() {
        return jwtConfig.getRefreshExpiryMs();
    }

    // ── Claims extraction ────────────────────────────────────────────────

    public String extractUsername(String token) {
        return extractAllClaims(token).getSubject();
    }

    public String extractRole(String token) {
        return extractAllClaims(token).get("role", String.class);
    }

    // ── Internal ─────────────────────────────────────────────────────────

    private String buildToken(Map<String, Object> claims, String subject, long expiryMs) {
        Date now    = new Date();
        Date expiry = new Date(now.getTime() + expiryMs);

        return Jwts.builder()
                .claims(claims)
                .subject(subject)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(getSigningKey())
                .compact();
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(
                jwtConfig.getSecret().getBytes(StandardCharsets.UTF_8)
        );
    }

}