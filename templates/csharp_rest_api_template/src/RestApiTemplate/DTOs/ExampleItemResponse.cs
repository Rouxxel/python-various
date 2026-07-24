using Template.RestApi.Entities;

namespace Template.RestApi.DTOs;

public sealed record ExampleItemResponse(string Id, string Name, string? Description)
{
    public static ExampleItemResponse From(ExampleItem item) => new(item.Id, item.Name, item.Description);
}
