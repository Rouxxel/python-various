/**
 * #############################################################################
 * ### Redis client
 * ###
 * ### @file RedisClient.java
 * ### @author Sebastian Russo
 * ### @date 2026
 * #############################################################################
 *
 * Creates an optional Redis connection when REDIS_ENABLED=true.
 * Connection failures are logged and never crash the application.
 */
package com.template.restapi.resources.cache;

import com.template.restapi.util.CustomLogger;

import jakarta.annotation.PreDestroy;

import org.springframework.stereotype.Component;

import redis.clients.jedis.DefaultJedisClientConfig;
import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.JedisPooled;

@Component
public class RedisClient {

    private final boolean enabled;
    private JedisPooled client;

    public RedisClient() {
        enabled = parseBool(System.getenv("REDIS_ENABLED"), false);
        if (!enabled) {
            CustomLogger.info("Redis is disabled (REDIS_ENABLED=false)");
            return;
        }

        String host = envOrDefault("REDIS_HOST", "localhost");
        int port = parseInt(System.getenv("REDIS_PORT"), 6379);
        int db = parseInt(System.getenv("REDIS_DB"), 0);
        String password = System.getenv("REDIS_PASSWORD");
        if (password != null && password.isBlank()) {
            password = null;
        }

        try {
            DefaultJedisClientConfig.Builder configBuilder = DefaultJedisClientConfig.builder()
                    .database(db)
                    .connectionTimeoutMillis(5000)
                    .socketTimeoutMillis(5000);
            if (password != null) {
                configBuilder.password(password);
            }

            client = new JedisPooled(new HostAndPort(host, port), configBuilder.build());
            client.ping();
            CustomLogger.info("Redis connected at " + host + ":" + port + "/" + db);
        } catch (Exception ex) {
            client = null;
            CustomLogger.warning("Redis connection failed: " + ex.getMessage() + ". Cache unavailable.");
        }
    }

    public boolean isAvailable() {
        return client != null;
    }

    /**
     * @return {@code disabled}, {@code connected}, or {@code unavailable}
     */
    public String getStatus() {
        if (!enabled) {
            return "disabled";
        }
        if (client == null) {
            return "unavailable";
        }
        try {
            client.ping();
            return "connected";
        } catch (Exception ex) {
            return "unavailable";
        }
    }

    public String get(String key) {
        if (client == null) {
            return null;
        }
        try {
            return client.get(key);
        } catch (Exception ex) {
            CustomLogger.warning("Redis GET failed for key '" + key + "': " + ex.getMessage());
            return null;
        }
    }

    public boolean setEx(String key, int expirationSeconds, String value) {
        if (client == null) {
            return false;
        }
        try {
            client.setex(key, expirationSeconds, value);
            return true;
        } catch (Exception ex) {
            CustomLogger.warning("Redis SETEX failed for key '" + key + "': " + ex.getMessage());
            return false;
        }
    }

    public boolean delete(String key) {
        if (client == null) {
            return false;
        }
        try {
            client.del(key);
            return true;
        } catch (Exception ex) {
            CustomLogger.warning("Redis DEL failed for key '" + key + "': " + ex.getMessage());
            return false;
        }
    }

    @PreDestroy
    public void close() {
        if (client != null) {
            try {
                client.close();
                CustomLogger.info("Redis connection closed");
            } catch (Exception ex) {
                CustomLogger.warning("Error closing Redis connection: " + ex.getMessage());
            }
        }
    }

    private static boolean parseBool(String value, boolean defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        return value.trim().equalsIgnoreCase("true")
                || value.trim().equals("1")
                || value.trim().equalsIgnoreCase("yes");
    }

    private static String envOrDefault(String key, String defaultValue) {
        String value = System.getenv(key);
        return value == null || value.isBlank() ? defaultValue : value;
    }

    private static int parseInt(String value, int defaultValue) {
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }
}
