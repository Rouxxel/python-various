using Template.RestApi.CoreSpecs.Configuration;

namespace Template.RestApi.Configuration;

/// <summary>Produces the configuration and host values derived from CoreSpecs.</summary>
public static class CoreSpecsConfigurationValues
{
    public static IReadOnlyDictionary<string, string?> Create(CoreSpecsConfiguration config)
    {
        var values = new Dictionary<string, string?>
        {
            ["CoreSpecs:Defaults:GeneralDataPath"] = config.Defaults.GeneralDataPath,
            ["CoreSpecs:Logging:LoggingLevel"] = config.Logging.LoggingLevel,
            ["CoreSpecs:Logging:DirectoryName"] = config.Logging.DirectoryName,
            ["CoreSpecs:Logging:LogFileName"] = config.Logging.LogFileName,
            ["CoreSpecs:Network:ServerPort"] = config.Network.ServerPort.ToString(),
            ["CoreSpecs:Network:Host"] = config.Network.Host,
            ["CoreSpecs:Network:ContextPath"] = config.Network.ContextPath
        };

        for (var index = 0; index < config.EmailValidation.AllowedProviders.Count; index++)
        {
            values[$"CoreSpecs:EmailValidation:AllowedProviders:{index}"] =
                config.EmailValidation.AllowedProviders[index];
        }

        for (var index = 0; index < config.EmailValidation.AllowedTlds.Count; index++)
        {
            values[$"CoreSpecs:EmailValidation:AllowedTlds:{index}"] =
                config.EmailValidation.AllowedTlds[index];
        }

        foreach (var (key, endpoint) in config.Endpoints)
        {
            var prefix = $"CoreSpecs:Endpoints:{key}";
            values[$"{prefix}:RequestLimit"] = endpoint.RequestLimit.ToString();
            values[$"{prefix}:UnitOfTimeForLimit"] = endpoint.UnitOfTimeForLimit;
            values[$"{prefix}:EndpointPrefix"] = endpoint.EndpointPrefix;
            values[$"{prefix}:EndpointTag"] = endpoint.EndpointTag;
            values[$"{prefix}:EndpointRoute"] = endpoint.EndpointRoute;
        }

        return values;
    }

    public static string GetHostUrl(NetworkConfiguration network) =>
        $"http://{network.Host}:{network.ServerPort}";
}
