using Template.RestApi.DTOs;
using Template.RestApi.Errors;
using Template.RestApi.Repositories;
using Template.RestApi.Resources.Cache;
using Template.RestApi.Services;

namespace Template.RestApi.Tests;

public sealed class ExampleItemServiceTests
{
    [Fact]
    public void ServiceSupportsCreateReadUpdateDelete()
    {
        var service = new ExampleItemService(
            new InMemoryExampleItemRepository(),
            new RedisCacheService(new RedisClient()));
        var initialCount = service.ListAll().Count;
        var created = service.Create(new ExampleItemCreate("item", "before"));

        Assert.Equal(initialCount + 1, service.ListAll().Count);
        Assert.Equal("before", service.GetById(created.Id).Description);
        Assert.Equal("after", service.Update(created.Id, new ExampleItemUpdate(null, "after")).Description);
        service.Delete(created.Id);
        Assert.Equal(initialCount, service.ListAll().Count);
        Assert.Throws<ResourceNotFoundException>(() => service.GetById(created.Id));
    }
}
