using Template.RestApi.Configuration;
using Template.RestApi.CoreSpecs.Configuration;
using Template.RestApi.Errors;

namespace Template.RestApi.Middleware;

public sealed class RateLimitMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context, ConfigLoader configLoader, RateLimiter rateLimiter)
    {
        var rateLimit = context.GetEndpoint()?.Metadata.GetMetadata<RateLimitAttribute>();
        if (rateLimit is not null)
        {
            var specification = configLoader.GetEndpoint(rateLimit.EndpointKey);
            var clientIp = context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
            if (!rateLimiter.IsAllowed(
                    clientIp,
                    rateLimit.EndpointKey,
                    specification.RequestLimit,
                    RateLimiter.WindowFor(specification.UnitOfTimeForLimit),
                    DateTimeOffset.UtcNow))
            {
                throw new RateLimitExceededException("Request rate limit exceeded. Please try again later.");
            }
        }

        await next(context);
    }
}
