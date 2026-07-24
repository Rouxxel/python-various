using System.Text.Json;

namespace Template.RestApi.CoreSpecs.Configuration;

/// <summary>Loads and validates the central API specification once at startup.</summary>
public sealed class ConfigLoader
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private ConfigLoader(CoreSpecsConfiguration configuration) => Configuration = configuration;

    public CoreSpecsConfiguration Configuration { get; }

    public static ConfigLoader Load(string path)
    {
        var fullPath = Path.GetFullPath(path);
        if (!File.Exists(fullPath))
        {
            throw new FileNotFoundException(
                $"CoreSpecs configuration file was not found: '{fullPath}'.", fullPath);
        }

        try
        {
            var configuration = JsonSerializer.Deserialize<CoreSpecsConfiguration>(
                File.ReadAllText(fullPath), JsonOptions)
                ?? throw new InvalidOperationException($"CoreSpecs configuration '{fullPath}' is empty.");

            Validate(configuration, fullPath);
            return new ConfigLoader(configuration);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"CoreSpecs configuration '{fullPath}' contains invalid JSON.", exception);
        }
    }

    public EndpointSpecification GetEndpoint(string endpointKey)
    {
        if (!Configuration.Endpoints.TryGetValue(endpointKey, out var endpoint))
        {
            throw new KeyNotFoundException(
                $"Endpoint key '{endpointKey}' was not found in CoreSpecs configuration.");
        }

        return endpoint;
    }

    private static void Validate(CoreSpecsConfiguration config, string path)
    {
        if (string.IsNullOrWhiteSpace(config.Defaults.GeneralDataPath) ||
            string.IsNullOrWhiteSpace(config.Logging.LoggingLevel) ||
            string.IsNullOrWhiteSpace(config.Logging.DirectoryName) ||
            string.IsNullOrWhiteSpace(config.Logging.LogFileName) ||
            string.IsNullOrWhiteSpace(config.Network.Host) ||
            config.Network.ServerPort is < 1 or > 65535 ||
            config.Endpoints.Count == 0)
        {
            throw new InvalidOperationException(
                $"CoreSpecs configuration '{path}' is missing one or more required values.");
        }

        foreach (var (key, endpoint) in config.Endpoints)
        {
            if (string.IsNullOrWhiteSpace(key) || endpoint.RequestLimit < 1 ||
                string.IsNullOrWhiteSpace(endpoint.UnitOfTimeForLimit) ||
                string.IsNullOrWhiteSpace(endpoint.EndpointRoute))
            {
                throw new InvalidOperationException(
                    $"CoreSpecs configuration '{path}' contains an invalid endpoint specification.");
            }
        }
    }
}
