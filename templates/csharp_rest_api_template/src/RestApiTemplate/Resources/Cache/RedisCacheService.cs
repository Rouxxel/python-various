using System.Text.Json;
using System.Text.Json.Serialization;

namespace Template.RestApi.Resources.Cache;

/// <summary>
/// Application-level cache helpers. Controllers and services should use this class
/// instead of importing <see cref="RedisClient"/> directly.
/// </summary>
public sealed class RedisCacheService(RedisClient redisClient)
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public T? CacheGet<T>(string key)
    {
        var raw = redisClient.Get(key);
        if (raw is null)
        {
            return default;
        }

        try
        {
            return JsonSerializer.Deserialize<T>(raw, JsonOptions);
        }
        catch (JsonException)
        {
            return default;
        }
    }

    public bool CacheSet<T>(string key, T value, int expirationSeconds)
    {
        try
        {
            var json = JsonSerializer.Serialize(value, JsonOptions);
            return redisClient.SetEx(key, expirationSeconds, json);
        }
        catch (NotSupportedException)
        {
            return false;
        }
    }

    public bool CacheDelete(string key) => redisClient.Delete(key);
}
