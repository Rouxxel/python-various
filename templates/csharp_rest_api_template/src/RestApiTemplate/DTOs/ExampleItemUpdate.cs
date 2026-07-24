using System.ComponentModel.DataAnnotations;

namespace Template.RestApi.DTOs;

public sealed record ExampleItemUpdate(
    [property: StringLength(200, MinimumLength = 1)] string? Name,
    [property: StringLength(2000)] string? Description);
