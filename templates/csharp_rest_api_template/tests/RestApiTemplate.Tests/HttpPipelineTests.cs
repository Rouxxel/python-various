using Microsoft.AspNetCore.Mvc.Testing;

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
        Assert.Equal(System.Net.HttpStatusCode.NotFound, (await client.GetAsync("/missing")).StatusCode);
    }
}
