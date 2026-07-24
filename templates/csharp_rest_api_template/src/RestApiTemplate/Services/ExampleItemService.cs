using Template.RestApi.DTOs;
using Template.RestApi.Entities;
using Template.RestApi.Errors;
using Template.RestApi.Repositories;
using Template.RestApi.Utils;

namespace Template.RestApi.Services;

public sealed class ExampleItemService(IExampleItemRepository repository)
{
    public IReadOnlyList<ExampleItemResponse> ListAll() => repository.FindAll().Select(ExampleItemResponse.From).ToList();
    public ExampleItemResponse GetById(string id) => ExampleItemResponse.From(Find(id));
    public ExampleItemResponse Create(ExampleItemCreate input)
    {
        var item = new ExampleItem(Guid.NewGuid().ToString(), input.Name, input.Description);
        repository.Save(item);
        CustomLogger.Info($"Created example item with id '{item.Id}'.");
        return ExampleItemResponse.From(item);
    }
    public ExampleItemResponse Update(string id, ExampleItemUpdate input)
    {
        var item = Find(id);
        if (input.Name is not null) item.Name = input.Name;
        if (input.Description is not null) item.Description = input.Description;
        repository.Save(item);
        return ExampleItemResponse.From(item);
    }
    public void Delete(string id)
    {
        if (!repository.DeleteById(id)) throw new ResourceNotFoundException($"Example item with id '{id}' was not found.");
    }
    private ExampleItem Find(string id) => repository.FindById(id) ?? throw new ResourceNotFoundException($"Example item with id '{id}' was not found.");
}
