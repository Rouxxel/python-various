using Microsoft.AspNetCore.Mvc;
using Template.RestApi.Configuration;
using Template.RestApi.CoreSpecs.Data;
using Template.RestApi.DTOs;
using Template.RestApi.Services;
using Template.RestApi.Utils;

namespace Template.RestApi.Controllers.ExampleGroupOne;

public sealed class ExampleItemsController(ExampleItemService service, DataLoader dataLoader) : ControllerBase
{
    [HttpGet]
    [RateLimit("example_endpoint_1")]
    public ActionResult<IReadOnlyList<ExampleItemResponse>> List()
    {
        CustomLogger.Debug($"Listing example items (languages: {string.Join(',', dataLoader.GetLanguages())}).");
        return Ok(service.ListAll());
    }
    [HttpGet]
    [RateLimit("example_endpoint_1")]
    public ActionResult<ExampleItemResponse> GetById(string id) => Ok(service.GetById(id));
    [HttpPost]
    [RateLimit("example_endpoint_1")]
    public ActionResult<ExampleItemResponse> Create([FromBody] ExampleItemCreate input, [FromQuery] string? contactEmail)
    {
        if (!string.IsNullOrWhiteSpace(contactEmail)) Validators.ValidateEmailFormat(contactEmail);
        return StatusCode(StatusCodes.Status201Created, service.Create(input));
    }
    [HttpPatch]
    [RateLimit("example_endpoint_1")]
    public ActionResult<ExampleItemResponse> Update(string id, [FromBody] ExampleItemUpdate input) => Ok(service.Update(id, input));
    [HttpDelete]
    [RateLimit("example_endpoint_1")]
    public IActionResult Delete(string id) { service.Delete(id); return NoContent(); }
}
