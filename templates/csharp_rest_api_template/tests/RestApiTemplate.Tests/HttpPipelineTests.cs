using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Template.RestApi.Entities;
using Template.RestApi.Repositories;

namespace Template.RestApi.Tests;

public sealed class HttpPipelineTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task CreateItemReturnsCreated()
    {
        using var client = factory.CreateClient();
        using var content = new StringContent("{\"name\":\"example\"}", System.Text.Encoding.UTF8, "application/json");
        var response = await client.PostAsync("/subsection/items", content);
        Assert.Equal(System.Net.HttpStatusCode.Created, response.StatusCode);
    }

    [Fact]
    public async Task RootHealthDocsAndNotFoundUseExpectedResponses()
    {
        using var client = factory.CreateClient();

        Assert.Equal(System.Net.HttpStatusCode.OK, (await client.GetAsync("/")).StatusCode);
        Assert.Equal(System.Net.HttpStatusCode.OK, (await client.GetAsync("/health")).StatusCode);
        Assert.Equal(System.Net.HttpStatusCode.OK, (await client.GetAsync("/api-docs/v1.json")).StatusCode);
        var missing = await client.GetAsync("/missing");
        Assert.Equal(System.Net.HttpStatusCode.NotFound, missing.StatusCode);
        Assert.Contains("\"status\":404", await missing.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task InvalidEmailReturnsUniformBadRequest()
    {
        using var client = factory.CreateClient();
        using var content = new StringContent("{\"name\":\"example\"}", System.Text.Encoding.UTF8, "application/json");
        var response = await client.PostAsync("/subsection/items?contactEmail=invalid", content);

        Assert.Equal(System.Net.HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Contains("\"status\":400", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task StatusEndpointReturns429AfterConfiguredLimit()
    {
        using var client = factory.CreateClient();
        for (var index = 0; index < 5; index++)
        {
            Assert.Equal(System.Net.HttpStatusCode.OK, (await client.GetAsync("/subsection/status")).StatusCode);
        }

        var limited = await client.GetAsync("/subsection/status");
        Assert.Equal((System.Net.HttpStatusCode)429, limited.StatusCode);
        Assert.Contains("\"status\":429", await limited.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task UnexpectedRepositoryFailureReturnsSanitized500()
    {
        using var failingFactory = factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                services.RemoveAll<IExampleItemRepository>();
                services.AddSingleton<IExampleItemRepository, ThrowingRepository>();
            }));
        using var client = failingFactory.CreateClient();
        using var content = new StringContent("{\"name\":\"example\"}", System.Text.Encoding.UTF8, "application/json");
        var response = await client.PostAsync("/subsection/items", content);

        Assert.Equal(System.Net.HttpStatusCode.InternalServerError, response.StatusCode);
        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("\"status\":500", body);
        Assert.DoesNotContain("repository failure", body, StringComparison.OrdinalIgnoreCase);
    }

    private sealed class ThrowingRepository : IExampleItemRepository
    {
        public IReadOnlyList<ExampleItem> FindAll() => throw new InvalidOperationException("repository failure");
        public ExampleItem? FindById(string id) => throw new InvalidOperationException("repository failure");
        public void Save(ExampleItem item) => throw new InvalidOperationException("repository failure");
        public bool DeleteById(string id) => throw new InvalidOperationException("repository failure");
    }
}
