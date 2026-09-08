package com.sentinel;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class SentinelBackendApplicationTests {

    @Test
    void contextLoads() {
        // Verifies the full Spring context starts cleanly on H2 + test profile.
        // No assertions needed — a startup failure will fail this test automatically.
    }
}