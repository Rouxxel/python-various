using Template.RestApi.Middleware;

namespace Template.RestApi.Tests;

public sealed class RateLimiterTests
{
    [Fact]
    public void EnforcesConfiguredLimitAndResetsAfterWindow()
    {
        var limiter = new RateLimiter();
        var now = DateTimeOffset.UtcNow;

        Assert.True(limiter.IsAllowed("127.0.0.1", "root", 2, TimeSpan.FromMinutes(1), now));
        Assert.True(limiter.IsAllowed("127.0.0.1", "root", 2, TimeSpan.FromMinutes(1), now));
        Assert.False(limiter.IsAllowed("127.0.0.1", "root", 2, TimeSpan.FromMinutes(1), now));
        Assert.True(limiter.IsAllowed("127.0.0.1", "root", 2, TimeSpan.FromMinutes(1), now.AddMinutes(1)));
    }

    [Theory]
    [InlineData("s", 1)]
    [InlineData("m", 60)]
    [InlineData("h", 3600)]
    [InlineData("d", 86400)]
    public void ConvertsConfiguredTimeUnits(string unit, int expectedSeconds) =>
        Assert.Equal(TimeSpan.FromSeconds(expectedSeconds), RateLimiter.WindowFor(unit));
}
