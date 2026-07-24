using Template.RestApi.CoreSpecs.Configuration;
using Template.RestApi.CoreSpecs.Data;
using Template.RestApi.Configuration;

namespace Template.RestApi.Tests;

public sealed class CoreSpecsTests : IDisposable
{
    private readonly string _rootPath = Path.Combine(Path.GetTempPath(), $"core-specs-{Guid.NewGuid():N}");

    public CoreSpecsTests() => Directory.CreateDirectory(_rootPath);

    [Fact]
    public void ConfigLoaderLoadsConfigurationAndFindsEndpoint()
    {
        var loader = ConfigLoader.Load(WriteConfig());

        var endpoint = loader.GetEndpoint("example_endpoint");

        Assert.Equal(8123, loader.Configuration.Network.ServerPort);
        Assert.Equal("/items", endpoint.EndpointRoute);
    }

    [Fact]
    public void ConfigLoaderReportsMissingFileAndEndpointKey()
    {
        var missingPath = Path.Combine(_rootPath, "missing.json");
        Assert.Throws<FileNotFoundException>(() => ConfigLoader.Load(missingPath));

        var loader = ConfigLoader.Load(WriteConfig());
        Assert.Throws<KeyNotFoundException>(() => loader.GetEndpoint("does_not_exist"));
    }

    [Fact]
    public void ConfigLoaderReportsInvalidJsonWithAnActionableError()
    {
        var path = Path.Combine(_rootPath, "invalid.json");
        File.WriteAllText(path, "{");

        var exception = Assert.Throws<InvalidOperationException>(() => ConfigLoader.Load(path));

        Assert.Contains("invalid JSON", exception.Message);
    }

    [Fact]
    public void DataLoaderReturnsStaticReferenceData()
    {
        var loader = DataLoader.Load(WriteData());

        Assert.Equal("Template Maintainer", loader.Data.Metadata.Maintainer);
        Assert.Equal(new[] { "en", "de" }, loader.GetLanguages());
    }

    [Fact]
    public void CoreSpecsValuesReflectEndpointChangesWithoutControllerChanges()
    {
        var loader = ConfigLoader.Load(WriteConfig());
        var values = CoreSpecsConfigurationValues.Create(loader.Configuration);

        Assert.Equal("/examples", values["CoreSpecs:Endpoints:example_endpoint:EndpointPrefix"]);
        Assert.Equal("/items", values["CoreSpecs:Endpoints:example_endpoint:EndpointRoute"]);
        Assert.Equal("http://127.0.0.1:8123",
            CoreSpecsConfigurationValues.GetHostUrl(loader.Configuration.Network));
    }

    public void Dispose()
    {
        if (Directory.Exists(_rootPath))
        {
            Directory.Delete(_rootPath, recursive: true);
        }
    }

    private string WriteConfig()
    {
        var path = Path.Combine(_rootPath, "config.json");
        File.WriteAllText(path, """
            {
              "defaults": { "general_data_path": "Resources/CoreSpecs/Data/general_data.json" },
              "logging": { "logging_level": "info", "dir_name": "logs", "log_file_name": "api" },
              "email_validation": { "allowed_providers": ["example"], "allowed_tlds": ["com"] },
              "network": { "server_port": 8123, "host": "127.0.0.1", "context_path": "" },
              "endpoints": {
                "example_endpoint": {
                  "request_limit": 5,
                  "unit_of_time_for_limit": "m",
                  "endpoint_prefix": "/examples",
                  "endpoint_tag": "examples",
                  "endpoint_route": "/items"
                }
              }
            }
            """);
        return path;
    }

    private string WriteData()
    {
        var path = Path.Combine(_rootPath, "data.json");
        File.WriteAllText(path, """
            {
              "metadata": { "maintainer": "Template Maintainer" },
              "languages": ["en", "de"]
            }
            """);
        return path;
    }
}
