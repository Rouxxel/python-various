using Template.RestApi.CoreSpecs.Configuration;
using Template.RestApi.Utils;
using UtilityLogLevel = Template.RestApi.Utils.LogLevel;

namespace Template.RestApi.Configuration;

/// <summary>Applies CoreSpecs values to the reusable C# utility helpers.</summary>
public static class UtilityStartup
{
    public static void Configure(CoreSpecsConfiguration configuration, string contentRootPath)
    {
        var logDirectory = Path.IsPathRooted(configuration.Logging.DirectoryName)
            ? configuration.Logging.DirectoryName
            : Path.Combine(contentRootPath, configuration.Logging.DirectoryName);

        CustomLogger.Setup(
            logDirectory,
            configuration.Logging.LogFileName,
            ParseLogLevel(configuration.Logging.LoggingLevel));

        Validators.SetEmailValidationConfig(
            configuration.EmailValidation.AllowedProviders,
            configuration.EmailValidation.AllowedTlds);

        SecureFileIo.SetAllowedRoot(Path.Combine(contentRootPath, "Resources"));
    }

    private static UtilityLogLevel ParseLogLevel(string configuredLevel)
    {
        if (Enum.TryParse<UtilityLogLevel>(configuredLevel, ignoreCase: true, out var level))
        {
            return level;
        }

        throw new InvalidOperationException(
            $"Unsupported logging level '{configuredLevel}' in CoreSpecs configuration.");
    }
}
