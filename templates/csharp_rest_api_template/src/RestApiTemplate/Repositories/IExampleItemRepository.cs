using Template.RestApi.Entities;

namespace Template.RestApi.Repositories;

public interface IExampleItemRepository
{
    IReadOnlyList<ExampleItem> FindAll();
    ExampleItem? FindById(string id);
    void Save(ExampleItem item);
    bool DeleteById(string id);
}
