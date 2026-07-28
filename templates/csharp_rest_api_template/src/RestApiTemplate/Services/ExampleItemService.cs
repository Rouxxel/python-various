using Template.RestApi.DTOs;
using Template.RestApi.Entities;
using Template.RestApi.Errors;
using Template.RestApi.Repositories;
using Template.RestApi.Resources.Cache;
using Template.RestApi.Utils;

namespace Template.RestApi.Services;

public sealed class ExampleItemService(IExampleItemRepository repository, RedisCacheService cacheService)
{
    private const string CacheKeyPrefix = "example_item:";
    private const int CacheTtlSeconds = 600;

    public IReadOnlyList<ExampleItemResponse> ListAll() => repository.FindAll().Select(ExampleItemResponse.From).ToList();

    public ExampleItemResponse GetById(string id)
    {
        var cacheKey = CacheKeyPrefix + id;
        var cached = cacheService.CacheGet<ExampleItemResponse>(cacheKey);
        if (cached is not null)
        {
            CustomLogger.Debug($"Cache hit for example item {id}");
            return cached;
        }

        var response = ExampleItemResponse.From(Find(id));
        cacheService.CacheSet(cacheKey, response, CacheTtlSeconds);
        CustomLogger.Debug($"Cache miss for example item {id}");
        return response;
    }

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
        cacheService.CacheDelete(CacheKeyPrefix + id);
        return ExampleItemResponse.From(item);
    }

    public void Delete(string id)
    {
        if (!repository.DeleteById(id))
        {
            throw new ResourceNotFoundException($"Example item with id '{id}' was not found.");
        }

        cacheService.CacheDelete(CacheKeyPrefix + id);
    }

    private ExampleItem Find(string id) => repository.FindById(id) ?? throw new ResourceNotFoundException($"Example item with id '{id}' was not found.");
}
