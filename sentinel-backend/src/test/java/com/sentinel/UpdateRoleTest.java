package com.sentinel;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

@SpringBootTest
public class UpdateRoleTest {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    public void updateAdminUser() {
        jdbcTemplate.update("UPDATE users SET role = 'ADMIN' WHERE username = 'adminuser'");
        System.out.println("User 'adminuser' updated to ADMIN.");
    }
}
