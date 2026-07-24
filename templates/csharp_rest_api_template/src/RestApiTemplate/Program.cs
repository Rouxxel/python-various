using Template.RestApi.Configuration;
using Template.RestApi.Utils;

if (args.Length > 0 && string.Equals(args[0], "--generate-rsa-keys", StringComparison.OrdinalIgnoreCase))
{
    var privateKeyPath = args.Length > 1 ? args[1] : "private_rsa_key.pem";
    var publicKeyPath = args.Length > 2 ? args[2] : "public_rsa_key.pem";
    KeysGenerator.GenerateRsaKeys(privateKeyPath, publicKeyPath);
    return;
}

var builder = WebApplication.CreateBuilder(args);

// CoreSpecs are loaded before the application is built so they can configure
// both the DI container and the host binding. Endpoint routing uses them later.
var coreSpecs = CoreSpecsConfigurationProvider.LoadAndApply(
    builder.Configuration,
    builder.Environment.ContentRootPath);
CoreSpecsConfigurationProvider.ConfigureWebHost(builder.WebHost, coreSpecs.Configuration.Network);
UtilityStartup.Configure(coreSpecs.Configuration, builder.Environment.ContentRootPath);

builder.Services.AddSingleton(coreSpecs.ConfigurationLoader);
builder.Services.AddSingleton(coreSpecs.DataLoader);
builder.Services.AddSingleton(coreSpecs.Configuration);
builder.Services.AddSingleton(coreSpecs.Data);
builder.Services.AddControllers();

var app = builder.Build();
app.Lifetime.ApplicationStopping.Register(CustomLogger.Shutdown);

// Configure the HTTP request pipeline.

app.UseAuthorization();

app.MapControllers();

app.Run();
