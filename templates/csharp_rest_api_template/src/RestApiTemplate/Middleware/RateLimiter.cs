using System.Collections.Concurrent;

namespace Template.RestApi.Middleware;

public sealed class RateLimiter
{
    private readonly ConcurrentDictionary<string, WindowCounter> _counters = new();

    public bool IsAllowed(string clientIp, string endpointKey, int limit, TimeSpan window, DateTimeOffset now)
    {
        var key = $"{clientIp}:{endpointKey}";
        var counter = _counters.GetOrAdd(key, _ => new WindowCounter(now, 0));

        lock (counter)
        {
            if (now - counter.WindowStart >= window)
            {
                counter.WindowStart = now;
                counter.Count = 0;
            }

            if (counter.Count >= limit)
            {
                return false;
            }

            counter.Count++;
        }

        foreach (var item in _counters.Where(item => now - item.Value.WindowStart >= window))
        {
            _counters.TryRemove(item.Key, out _);
        }

        return true;
    }

    public static TimeSpan WindowFor(string unit) => unit.ToLowerInvariant() switch
    {
        "s" => TimeSpan.FromSeconds(1),
        "m" => TimeSpan.FromMinutes(1),
        "h" => TimeSpan.FromHours(1),
        "d" => TimeSpan.FromDays(1),
        _ => throw new ArgumentException($"Unsupported rate-limit time unit '{unit}'.")
    };

    private sealed class WindowCounter(DateTimeOffset windowStart, int count)
    {
        public DateTimeOffset WindowStart { get; set; } = windowStart;
        public int Count { get; set; } = count;
    }
}
