using Microsoft.AspNetCore.Mvc.Testing;

namespace Template.RestApi.Tests;

public sealed class HttpPipelineTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
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
