using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;

namespace Template.RestApi.Controllers;

[ApiController]
[Route("")]
public sealed class RootController : ControllerBase
{
    [HttpGet("")]
    [RateLimit("root_directory_endpoint")]
    public IActionResult Get() => Ok(new { status = "healthy" });
}
