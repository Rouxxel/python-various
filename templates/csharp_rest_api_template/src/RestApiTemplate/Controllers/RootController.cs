using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;
using Template.RestApi.Utils;

namespace Template.RestApi.Controllers;

[ApiController]
[Route("")]
public sealed class RootController : ControllerBase
{
    [HttpGet("")]
    [RateLimit("root_directory_endpoint")]
    public IActionResult Get()
    {
        CustomLogger.Info("Root health check requested; API is healthy.");
        return Ok(new { status = "healthy" });
    }
}
