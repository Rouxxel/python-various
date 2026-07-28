/**
 * #############################################################################
 * ### Redis cache service
 * ###
 * ### @file RedisCacheService.java
 * ### @author Sebastian Russo
 * ### @date 2026
 * #############################################################################
 *
 * Application-level cache helpers. Controllers and services should use this
 * class instead of importing {@link RedisClient} directly.
 */
package com.template.restapi.resources.cache;

import java.util.Optional;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.springframework.stereotype.Service;

@Service
public class RedisCacheService {

    private final RedisClient redisClient;
    private final ObjectMapper objectMapper;

    public RedisCacheService(RedisClient redisClient, ObjectMapper objectMapper) {
        this.redisClient = redisClient;
        this.objectMapper = objectMapper;
    }

    public <T> Optional<T> cacheGet(String key, Class<T> type) {
        String raw = redisClient.get(key);
        if (raw == null) {
            return Optional.empty();
        }
        try {
            return Optional.of(objectMapper.readValue(raw, type));
        } catch (JsonProcessingException ex) {
            return Optional.empty();
        }
    }

    public boolean cacheSet(String key, Object value, int expirationSeconds) {
        try {
            String json = objectMapper.writeValueAsString(value);
            return redisClient.setEx(key, expirationSeconds, json);
        } catch (JsonProcessingException ex) {
            return false;
        }
    }

    public boolean cacheDelete(String key) {
        return redisClient.delete(key);
    }
}
