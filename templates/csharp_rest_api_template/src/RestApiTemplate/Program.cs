using Template.RestApi.Configuration;

var builder = WebApplication.CreateBuilder(args);

// CoreSpecs are loaded before the application is built so they can configure
// both the DI container and the host binding. Endpoint routing uses them later.
var coreSpecs = CoreSpecsConfigurationProvider.LoadAndApply(
    builder.Configuration,
    builder.Environment.ContentRootPath);
CoreSpecsConfigurationProvider.ConfigureWebHost(builder.WebHost, coreSpecs.Configuration.Network);

builder.Services.AddSingleton(coreSpecs.ConfigurationLoader);
builder.Services.AddSingleton(coreSpecs.DataLoader);
builder.Services.AddSingleton(coreSpecs.Configuration);
builder.Services.AddSingleton(coreSpecs.Data);
builder.Services.AddControllers();

var app = builder.Build();

// Configure the HTTP request pipeline.

app.UseAuthorization();

app.MapControllers();

app.Run();
