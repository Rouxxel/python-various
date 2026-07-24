using System.Collections.Concurrent;
using Template.RestApi.Entities;

namespace Template.RestApi.Repositories;

public sealed class InMemoryExampleItemRepository : IExampleItemRepository
{
    private readonly ConcurrentDictionary<string, ExampleItem> _items = new();
    public IReadOnlyList<ExampleItem> FindAll() => _items.Values.ToList();
    public ExampleItem? FindById(string id) => _items.GetValueOrDefault(id);
    public void Save(ExampleItem item) => _items[item.Id] = item;
    public bool DeleteById(string id) => _items.TryRemove(id, out _);
}
