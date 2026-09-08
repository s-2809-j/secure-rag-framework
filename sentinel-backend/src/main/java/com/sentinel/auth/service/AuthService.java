package com.sentinel.auth.service;

import com.sentinel.auth.dto.LoginRequest;
import com.sentinel.auth.dto.LoginResponse;
import com.sentinel.auth.dto.RefreshTokenRequest;
import com.sentinel.auth.dto.RegisterRequest;
import com.sentinel.auth.model.RefreshToken;
import com.sentinel.auth.model.Role;
import com.sentinel.auth.model.User;
import com.sentinel.auth.repository.RefreshTokenRepository;
import com.sentinel.auth.repository.UserRepository;
import com.sentinel.exception.UnauthorizedException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@Transactional
public class AuthService {

    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;
    private final PasswordEncoder passwordEncoder;

    public void register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.username())) {
            throw new com.sentinel.exception.SentinelException("USERNAME_CONFLICT", "Username already exists");
        }
        User user = User.builder()
                .username(request.username())
                .email(request.email())
                .passwordHash(passwordEncoder.encode(request.password()))
                .role(Role.VIEWER)
                .active(true)
                .build();
        userRepository.save(user);
    }

    public LoginResponse login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.username(), request.password())
        );
        User user = userRepository.findByUsername(request.username())
                .orElseThrow(() -> new UnauthorizedException("User not found"));

        refreshTokenRepository.revokeAllByUser(user);

        return issueTokenPair(user);
    }

    public LoginResponse refresh(RefreshTokenRequest request) {
        String token = request.refreshToken();

        if (!jwtService.isRefreshToken(token)) {
            throw new UnauthorizedException("Invalid token type");
        }

        String username = jwtService.extractUsername(token);
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UnauthorizedException("User not found"));

        RefreshToken stored = refreshTokenRepository
                .findByTokenAndRevokedFalse(token)
                .orElseThrow(() ->
                        new UnauthorizedException("Refresh token not found or revoked"));

        if (stored.getExpiresAt().isBefore(Instant.now())) {
            stored.setRevoked(true);
            refreshTokenRepository.save(stored);
            throw new UnauthorizedException("Refresh token expired");
        }

        stored.setRevoked(true);
        refreshTokenRepository.save(stored);

        try {
            return issueTokenPair(user);
        } catch (Exception ex) {
            // If token issuance fails, un-revoke so the user is not locked out.
            stored.setRevoked(false);
            refreshTokenRepository.save(stored);
            throw ex;
        }
    }

    public void logout(String username) {
        userRepository.findByUsername(username)
                .ifPresent(refreshTokenRepository::revokeAllByUser);
    }

    private LoginResponse issueTokenPair(User user) {
        String accessToken  = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        RefreshToken entity = RefreshToken.builder()
                .user(user)
                .token(refreshToken)
                .expiresAt(Instant.now().plusMillis(jwtService.getRefreshExpiryMs()))
                .revoked(false)
                .build();
        refreshTokenRepository.save(entity);

        return LoginResponse.of(
                accessToken,
                refreshToken,
                jwtService.getAccessExpiryMs(),
                user.getUsername(),
                user.getRole().name()
        );
    }
}