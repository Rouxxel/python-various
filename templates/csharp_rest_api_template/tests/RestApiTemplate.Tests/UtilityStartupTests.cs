using Template.RestApi.Configuration;
using Template.RestApi.CoreSpecs.Configuration;
using Template.RestApi.Utils;

namespace Template.RestApi.Tests;

public sealed class UtilityStartupTests : IDisposable
{
    private readonly string _rootPath = Path.Combine(Path.GetTempPath(), $"template-utils-{Guid.NewGuid():N}");

    public UtilityStartupTests() => Directory.CreateDirectory(_rootPath);

    [Fact]
    public void LoggerSetupCreatesAFileWithoutBlockingStartup()
    {
        var logDirectory = Path.Combine(_rootPath, "logs");

        CustomLogger.Setup(logDirectory, "template", LogLevel.Info);
        CustomLogger.Info("Logger startup verification.");
        CustomLogger.Shutdown();

        Assert.NotEmpty(Directory.GetFiles(logDirectory, "template_*.log"));
    }

    [Fact]
    public void UtilityStartupConfiguresValidatorsAndConfinesSecureFileIo()
    {
        var configuration = CreateConfiguration();
        Directory.CreateDirectory(Path.Combine(_rootPath, "Resources"));

        UtilityStartup.Configure(configuration, _rootPath);

        Validators.ValidateEmailFormat("person@example.com");
        Assert.Throws<ValidationException>(() => Validators.ValidateEmailFormat("person@example.invalid"));

        var safePath = Path.Combine(_rootPath, "Resources", "safe.txt");
        SecureFileIo.WriteText(safePath, "safe");
        Assert.Equal("safe", SecureFileIo.ReadText(safePath));

        var unsafePath = Path.Combine(_rootPath, "outside.txt");
        Assert.Throws<PathSecurityError>(() => SecureFileIo.WriteText(unsafePath, "unsafe"));
    }

    public void Dispose()
    {
        CustomLogger.Shutdown();
        SecureFileIo.SetAllowedRoot(null);
        if (Directory.Exists(_rootPath))
        {
            Directory.Delete(_rootPath, recursive: true);
        }
    }

    private static CoreSpecsConfiguration CreateConfiguration() => new(
        new DefaultsConfiguration("Resources/CoreSpecs/Data/general_data.json"),
        new LoggingConfiguration("info", "logs", "template"),
        new EmailValidationConfiguration(new[] { "example" }, new[] { "com" }),
        new NetworkConfiguration(8080, "127.0.0.1", string.Empty),
        new Dictionary<string, EndpointSpecification>
        {
            ["root"] = new(1, "m", string.Empty, "root", "/")
        });
}
