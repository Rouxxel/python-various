using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;
using Template.RestApi.Utils;

namespace Template.RestApi.Controllers.ExampleGroupTwo;

public sealed class ExampleStatusController : ControllerBase
{
    [HttpGet]
    [RateLimit("example_endpoint_2")]
    public IActionResult Get()
    {
        CustomLogger.Info("Example status endpoint requested; status is ok.");
        return Ok(new { status = "ok" });
    }
}
