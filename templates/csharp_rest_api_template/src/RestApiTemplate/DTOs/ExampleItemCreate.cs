using System.ComponentModel.DataAnnotations;

namespace Template.RestApi.DTOs;

public sealed record ExampleItemCreate(
    [param: Required(AllowEmptyStrings = false, ErrorMessage = "name must not be blank")]
    [param: StringLength(200, MinimumLength = 1)] string Name,
    [param: StringLength(2000)] string? Description);
