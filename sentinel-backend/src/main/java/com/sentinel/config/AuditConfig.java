package com.sentinel.config;

import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

@Configuration
@EnableAspectJAutoProxy
@EnableCaching
public class AuditConfig {

    // Activates @Aspect scanning — AuditAspect is picked up automatically
    // via @Component on the aspect class itself

    @Bean
    public org.springframework.cache.CacheManager cacheManager() {
        return new org.springframework.cache.concurrent.ConcurrentMapCacheManager(
                "rolePermissions"
        );
    }
}