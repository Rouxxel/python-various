using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;
using Template.RestApi.Resources.Cache;
using Template.RestApi.Utils;

namespace Template.RestApi.Controllers;

[ApiController]
[Route("")]
public sealed class RootController(RedisClient redisClient) : ControllerBase
{
    [HttpGet("")]
    [RateLimit("root_directory_endpoint")]
    public IActionResult Get()
    {
        CustomLogger.Info("Root health check requested; API is healthy.");
        return Ok(new
        {
            status = "ok",
            message = "Backend running successfully, ready to use other endpoints",
            redis = redisClient.GetStatus(),
        });
    }
}
