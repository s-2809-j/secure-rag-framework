package com.sentinel.chat;

import com.fasterxml.jackson.databind.ObjectMapper;

import com.sentinel.auth.filter.JwtAuthenticationFilter;
import com.sentinel.auth.service.JwtService;
import com.sentinel.chat.controller.ChatController;
import com.sentinel.chat.dto.ChatRequest;
import com.sentinel.chat.dto.ChatResponse;
import com.sentinel.chat.service.ChatService;
import com.sentinel.exception.ForbiddenException;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;

import static org.mockito.BDDMockito.given;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ChatController.class)
@AutoConfigureMockMvc(addFilters = false)
class ChatControllerTest {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @MockitoBean
    ChatService chatService;

    @MockitoBean
    JwtAuthenticationFilter jwtAuthenticationFilter;

    @MockitoBean
    JwtService jwtService;

    @MockitoBean
    UserDetailsService userDetailsService;

    private static final String ENDPOINT = "/api/v1/chat";

    private ChatResponse sampleChatResponse() {
        return new ChatResponse(
                UUID.randomUUID().toString(),
                true,
                "Here is your answer.",
                null,
                UUID.randomUUID().toString(),
                Instant.now()
        );
    }

    // ─────────────────────────────────────────────────────────────
    // HAPPY PATH
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Successful chat requests")
    class HappyPathTests {

        @Test
        @WithMockUser(username = "analyst@sentinel.io", roles = "ANALYST")
        @DisplayName("200 with ChatResponse when ANALYST sends valid query")
        void chat_returns200ForAnalyst() throws Exception {
            ChatRequest body = new ChatRequest("What is the threat model?", null);
            given(chatService.processChat(any(ChatRequest.class)))
                    .willReturn(sampleChatResponse());

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(body)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.message").value("Here is your answer."))
                    .andExpect(jsonPath("$.requestId").exists())
                    .andExpect(jsonPath("$.sessionId").exists());
        }

        @Test
        @WithMockUser(username = "admin@sentinel.io", roles = "ADMIN")
        @DisplayName("200 with ChatResponse when ADMIN sends valid query")
        void chat_returns200ForAdmin() throws Exception {
            ChatRequest body = new ChatRequest("List active threats.", null);
            given(chatService.processChat(any(ChatRequest.class)))
                    .willReturn(sampleChatResponse());

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(body)))
                    .andExpect(status().isOk());
        }

        @Test
        @WithMockUser(username = "viewer@sentinel.io", roles = "VIEWER")
        @DisplayName("200 with ChatResponse when VIEWER sends valid query")
        void chat_returns200ForViewer() throws Exception {
            ChatRequest body = new ChatRequest("Show summary.", null);
            given(chatService.processChat(any(ChatRequest.class)))
                    .willReturn(sampleChatResponse());

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(body)))
                    .andExpect(status().isOk());
        }

        @Test
        @WithMockUser(username = "analyst@sentinel.io", roles = "ANALYST")
        @DisplayName("200 with existing sessionId forwarded in response")
        void chat_forwardsSessionIdWhenProvided() throws Exception {
            String existingSession = UUID.randomUUID().toString();
            ChatRequest body = new ChatRequest("Follow-up question.", existingSession);

            ChatResponse responseWithSession = new ChatResponse(
                    UUID.randomUUID().toString(),
                    true,
                    "Follow-up answer.",
                    null,
                    existingSession,
                    Instant.now()
            );
            given(chatService.processChat(any(ChatRequest.class)))
                    .willReturn(responseWithSession);

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(body)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.sessionId").value(existingSession));
        }
    }

    // ─────────────────────────────────────────────────────────────
    // VALIDATION FAILURES
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Validation failures")
    class ValidationTests {

        @Test
        @WithMockUser(roles = "ANALYST")
        @DisplayName("400 when query is blank")
        void chat_returns400ForBlankQuery() throws Exception {
            ChatRequest bad = new ChatRequest("", null);

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(bad)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.errorCode").exists());
        }

        @Test
        @WithMockUser(roles = "ANALYST")
        @DisplayName("400 when query exceeds 4000 characters")
        void chat_returns400ForQueryExceedingMaxLength() throws Exception {
            ChatRequest bad = new ChatRequest("A".repeat(4001), null);

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(bad)))
                    .andExpect(status().isBadRequest());
        }
    }

    // ─────────────────────────────────────────────────────────────
    // AUTH / AUTHZ FAILURES
    // ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Auth and authz failures")
    class AuthTests {

//        @Test
//        @DisplayName("401 when request has no authentication")
//        void chat_returns401ForUnauthenticatedRequest() throws Exception {
//            ChatRequest body = new ChatRequest("Query without auth.", null);
//
//            mockMvc.perform(post(ENDPOINT)
//                            .with(csrf())
//                            .contentType(MediaType.APPLICATION_JSON)
//                            .content(objectMapper.writeValueAsString(body)))
//                    .andExpect(status().isUnauthorized());
//        }

        @Test
        @WithMockUser(roles = "ANALYST")
        @DisplayName("403 when ChatService throws ForbiddenException (e.g. content policy block)")
        void chat_returns403WhenServiceBlocksRequest() throws Exception {
            ChatRequest body = new ChatRequest("Sensitive query.", null);
            given(chatService.processChat(any(ChatRequest.class)))
                    .willThrow(new ForbiddenException("Content blocked by policy"));

            mockMvc.perform(post(ENDPOINT)
                            .with(csrf())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(body)))
                    .andExpect(status().isForbidden())
                    .andExpect(jsonPath("$.errorCode").value("FORBIDDEN"));
        }
    }
}