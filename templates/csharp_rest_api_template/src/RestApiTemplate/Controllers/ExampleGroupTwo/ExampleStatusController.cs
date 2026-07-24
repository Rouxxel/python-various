using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;

namespace Template.RestApi.Controllers.ExampleGroupTwo;

[Tags("example-status")]
public sealed class ExampleStatusController : ControllerBase
{
    [HttpGet]
    [RateLimit("example_endpoint_2")]
    public IActionResult Get() => Ok(new { status = "ok" });
}
