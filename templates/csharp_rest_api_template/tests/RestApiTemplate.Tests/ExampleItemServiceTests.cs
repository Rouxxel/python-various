using Template.RestApi.DTOs;
using Template.RestApi.Errors;
using Template.RestApi.Repositories;
using Template.RestApi.Services;

namespace Template.RestApi.Tests;

public sealed class ExampleItemServiceTests
{
    [Fact]
    public void ServiceSupportsCreateReadUpdateDelete()
    {
        var service = new ExampleItemService(new InMemoryExampleItemRepository());
        var created = service.Create(new ExampleItemCreate("item", "before"));

        Assert.Single(service.ListAll());
        Assert.Equal("before", service.GetById(created.Id).Description);
        Assert.Equal("after", service.Update(created.Id, new ExampleItemUpdate(null, "after")).Description);
        service.Delete(created.Id);
        Assert.Empty(service.ListAll());
        Assert.Throws<ResourceNotFoundException>(() => service.GetById(created.Id));
    }
}
