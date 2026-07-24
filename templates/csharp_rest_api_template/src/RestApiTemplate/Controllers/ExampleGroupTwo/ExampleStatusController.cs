using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;

namespace Template.RestApi.Controllers.ExampleGroupTwo;

public sealed class ExampleStatusController : ControllerBase
{
    [HttpGet]
    [RateLimit("example_endpoint_2")]
    public IActionResult Get() => Ok(new { status = "ok" });
}
