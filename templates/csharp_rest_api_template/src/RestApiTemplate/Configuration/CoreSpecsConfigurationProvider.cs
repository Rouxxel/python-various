using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Template.RestApi.CoreSpecs.Configuration;
using Template.RestApi.CoreSpecs.Data;

namespace Template.RestApi.Configuration;

/// <summary>
/// Bridges the template's JSON CoreSpecs into dependency injection, configuration
/// keys, and the ASP.NET Core host before the application is built.
/// </summary>
public static class CoreSpecsConfigurationProvider
{
    public const string ConfigurationRelativePath = "Resources/CoreSpecs/Configuration/config_file.json";

    public static CoreSpecsBootstrap LoadAndApply(
        ConfigurationManager configuration,
        string contentRootPath)
    {
        var configurationPath = Path.Combine(contentRootPath, ConfigurationRelativePath);
        var configurationLoader = ConfigLoader.Load(configurationPath);
        var dataPath = ResolvePath(contentRootPath, configurationLoader.Configuration.Defaults.GeneralDataPath);
        var dataLoader = DataLoader.Load(dataPath);

        configuration.AddInMemoryCollection(
            CoreSpecsConfigurationValues.Create(configurationLoader.Configuration));

        return new CoreSpecsBootstrap(configurationLoader, dataLoader, configurationPath, dataPath);
    }

    public static void ConfigureWebHost(IWebHostBuilder webHost, NetworkConfiguration network)
    {
        webHost.UseUrls(CoreSpecsConfigurationValues.GetHostUrl(network));
    }

    private static string ResolvePath(string contentRootPath, string configuredPath) =>
        Path.IsPathRooted(configuredPath)
            ? configuredPath
            : Path.Combine(contentRootPath, configuredPath);

}

public sealed record CoreSpecsBootstrap(
    ConfigLoader ConfigurationLoader,
    DataLoader DataLoader,
    string ConfigurationPath,
    string DataPath)
{
    public CoreSpecsConfiguration Configuration => ConfigurationLoader.Configuration;

    public GeneralData Data => DataLoader.Data;
}
