namespace Template.RestApi.Entities;

public sealed class ExampleItem(string id, string name, string? description)
{
    public string Id { get; } = id;
    public string Name { get; set; } = name;
    public string? Description { get; set; } = description;
}
