using System.ComponentModel.DataAnnotations;

namespace Template.RestApi.DTOs;

public sealed record ExampleItemUpdate(
    [param: StringLength(200, MinimumLength = 1)] string? Name,
    [param: StringLength(2000)] string? Description);
