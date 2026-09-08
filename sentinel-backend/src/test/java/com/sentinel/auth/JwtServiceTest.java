package com.sentinel.auth;

import com.sentinel.auth.model.Role;
import com.sentinel.auth.model.User;
import com.sentinel.auth.service.JwtService;
import com.sentinel.config.JwtConfig;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("JwtService Unit Tests")
class JwtServiceTest {

    private JwtService jwtService;
    private User testUser;

    @BeforeEach
    void setUp() {
        JwtConfig jwtConfig = new JwtConfig();
        jwtConfig.setSecret("dGVzdC1zZWNyZXQta2V5LXRoYXQtaXMtYXQtbGVhc3QtMjU2LWJpdHMtbG9uZy1mb3ItdGVzdGluZw==");
        jwtConfig.setAccessExpiryMs(900_000L);   // 15 min
        jwtConfig.setRefreshExpiryMs(604_800_000L); // 7 days

        jwtService = new JwtService(jwtConfig);

        testUser = User.builder()
                .id(UUID.randomUUID())
                .username("analyst@sentinel.io")
                .passwordHash("irrelevant-for-jwt-tests")
                .role(Role.ANALYST)
                .active(true)
                .build();
    }

    // ─────────────────────────────────────────────────────────────
    // ACCESS TOKEN
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Access Token")
    class AccessTokenTests {

        @Test
        @DisplayName("generateAccessToken returns non-blank JWT")
        void generateAccessToken_returnsNonBlankJwt() {
            String token = jwtService.generateAccessToken(testUser);
            assertThat(token).isNotBlank();
            assertThat(token.split("\\.")).hasSize(3); // header.payload.signature
        }

        @Test
        @DisplayName("extractUsername returns the subject embedded in access token")
        void extractUsername_returnsSubjectFromAccessToken() {
            String token = jwtService.generateAccessToken(testUser);
            assertThat(jwtService.extractUsername(token)).isEqualTo(testUser.getUsername());
        }

        @Test
        @DisplayName("isTokenValid returns true for a fresh access token belonging to the user")
        void isTokenValid_trueForFreshAccessToken() {
            String token = jwtService.generateAccessToken(testUser);
            assertThat(jwtService.isTokenValid(token)).isTrue();
        }

        @Test
        @DisplayName("isAccessToken returns true for access token and false for refresh token")
        void isAccessToken_discriminatesBetweenTokenTypes() {
            String access  = jwtService.generateAccessToken(testUser);
            String refresh = jwtService.generateRefreshToken(testUser);

            assertThat(jwtService.isAccessToken(access)).isTrue();
            assertThat(jwtService.isAccessToken(refresh)).isFalse();
        }



        @Test
        @DisplayName("isTokenValid returns false for tampered token")
        void isTokenValid_falseForTamperedToken() {
            String token = jwtService.generateAccessToken(testUser);
            String tampered = token.substring(0, token.length() - 4) + "XXXX";
            assertThat(jwtService.isTokenValid(tampered)).isFalse();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // REFRESH TOKEN
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Refresh Token")
    class RefreshTokenTests {

        @Test
        @DisplayName("generateRefreshToken returns non-blank JWT with type=refresh")
        void generateRefreshToken_returnsNonBlankJwt() {
            String token = jwtService.generateRefreshToken(testUser);
            assertThat(token).isNotBlank();
            assertThat(token.split("\\.")).hasSize(3);
        }

        @Test
        @DisplayName("refresh token subject matches username")
        void refreshToken_subjectMatchesUsername() {
            String token = jwtService.generateRefreshToken(testUser);
            assertThat(jwtService.extractUsername(token)).isEqualTo(testUser.getUsername());
        }

        @Test
        @DisplayName("isAccessToken is false for refresh token")
        void isAccessToken_falseForRefreshToken() {
            String token = jwtService.generateRefreshToken(testUser);
            assertThat(jwtService.isAccessToken(token)).isFalse();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // EXPIRED TOKEN (short-circuit config)
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Expired Token")
    class ExpiredTokenTests {

        @Test
        @DisplayName("isTokenValid returns false for an already-expired access token")
        void isTokenValid_falseForExpiredToken() {
            // Build a JwtService with 0ms expiry to force immediate expiry
            JwtConfig expiredConfig = new JwtConfig();
            expiredConfig.setSecret("dGVzdC1zZWNyZXQta2V5LXRoYXQtaXMtYXQtbGVhc3QtMjU2LWJpdHMtbG9uZy1mb3ItdGVzdGluZw==");
            expiredConfig.setAccessExpiryMs(0L);
            expiredConfig.setRefreshExpiryMs(0L);

            JwtService expiredJwtService = new JwtService(expiredConfig);
            String token = expiredJwtService.generateAccessToken(testUser);

            // Token is expired the moment it's created
            assertThat(expiredJwtService.isTokenValid(token)).isFalse();
        }
    }
}