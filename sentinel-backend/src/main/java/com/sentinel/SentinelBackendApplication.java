package com.sentinel;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableFeignClients(basePackages = "com.sentinel.fastapi.client")
@EnableAsync
public class SentinelBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(SentinelBackendApplication.class, args);
    }
}