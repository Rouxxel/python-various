using System.ComponentModel.DataAnnotations;

namespace Template.RestApi.DTOs;

public sealed record ExampleItemCreate(
    [property: Required(AllowEmptyStrings = false, ErrorMessage = "name must not be blank")]
    [property: StringLength(200, MinimumLength = 1)] string Name,
    [property: StringLength(2000)] string? Description);
