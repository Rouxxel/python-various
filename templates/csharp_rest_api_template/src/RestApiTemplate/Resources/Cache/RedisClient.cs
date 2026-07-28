using StackExchange.Redis;
using Template.RestApi.Utils;

namespace Template.RestApi.Resources.Cache;

/// <summary>
/// Creates an optional Redis connection when REDIS_ENABLED=true.
/// Connection failures are logged and never crash the application.
/// </summary>
public sealed class RedisClient : IDisposable
{
    private readonly bool _enabled;
    private ConnectionMultiplexer? _multiplexer;
    private IDatabase? _database;

    public RedisClient()
    {
        _enabled = ParseBool(Environment.GetEnvironmentVariable("REDIS_ENABLED"), false);
        if (!_enabled)
        {
            CustomLogger.Info("Redis is disabled (REDIS_ENABLED=false)");
            return;
        }

        var host = EnvOrDefault("REDIS_HOST", "localhost");
        var port = ParseInt(Environment.GetEnvironmentVariable("REDIS_PORT"), 6379);
        var db = ParseInt(Environment.GetEnvironmentVariable("REDIS_DB"), 0);
        var password = Environment.GetEnvironmentVariable("REDIS_PASSWORD");

        try
        {
            var options = new ConfigurationOptions
            {
                EndPoints = { { host, port } },
                DefaultDatabase = db,
                ConnectTimeout = 5000,
                SyncTimeout = 5000,
                AbortOnConnectFail = false,
            };
            if (!string.IsNullOrWhiteSpace(password))
            {
                options.Password = password;
            }

            _multiplexer = ConnectionMultiplexer.Connect(options);
            _database = _multiplexer.GetDatabase();
            _database.Ping();
            CustomLogger.Info($"Redis connected at {host}:{port}/{db}");
        }
        catch (Exception ex)
        {
            _multiplexer?.Dispose();
            _multiplexer = null;
            _database = null;
            CustomLogger.Warning($"Redis connection failed: {ex.Message}. Cache unavailable.");
        }
    }

    /// <returns><c>disabled</c>, <c>connected</c>, or <c>unavailable</c>.</returns>
    public string GetStatus()
    {
        if (!_enabled)
        {
            return "disabled";
        }

        if (_database is null)
        {
            return "unavailable";
        }

        try
        {
            _database.Ping();
            return "connected";
        }
        catch
        {
            return "unavailable";
        }
    }

    public string? Get(string key)
    {
        if (_database is null)
        {
            return null;
        }

        try
        {
            return _database.StringGet(key);
        }
        catch (Exception ex)
        {
            CustomLogger.Warning($"Redis GET failed for key '{key}': {ex.Message}");
            return null;
        }
    }

    public bool SetEx(string key, int expirationSeconds, string value)
    {
        if (_database is null)
        {
            return false;
        }

        try
        {
            return _database.StringSet(key, value, TimeSpan.FromSeconds(expirationSeconds));
        }
        catch (Exception ex)
        {
            CustomLogger.Warning($"Redis SET failed for key '{key}': {ex.Message}");
            return false;
        }
    }

    public bool Delete(string key)
    {
        if (_database is null)
        {
            return false;
        }

        try
        {
            return _database.KeyDelete(key);
        }
        catch (Exception ex)
        {
            CustomLogger.Warning($"Redis DEL failed for key '{key}': {ex.Message}");
            return false;
        }
    }

    public void Dispose()
    {
        if (_multiplexer is not null)
        {
            try
            {
                _multiplexer.Dispose();
                CustomLogger.Info("Redis connection closed");
            }
            catch (Exception ex)
            {
                CustomLogger.Warning($"Error closing Redis connection: {ex.Message}");
            }
        }
    }

    private static bool ParseBool(string? value, bool defaultValue) =>
        value switch
        {
            null => defaultValue,
            _ when value.Equals("true", StringComparison.OrdinalIgnoreCase) => true,
            _ when value.Equals("1", StringComparison.Ordinal) => true,
            _ when value.Equals("yes", StringComparison.OrdinalIgnoreCase) => true,
            _ => defaultValue,
        };

    private static string EnvOrDefault(string key, string defaultValue)
    {
        var value = Environment.GetEnvironmentVariable(key);
        return string.IsNullOrWhiteSpace(value) ? defaultValue : value;
    }

    private static int ParseInt(string? value, int defaultValue) =>
        int.TryParse(value, out var parsed) ? parsed : defaultValue;
}
