using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Template.RestApi.Configuration;
using Template.RestApi.Errors;
using Template.RestApi.Middleware;
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
builder.Services.Configure<ApiBehaviorOptions>(options =>
    options.InvalidModelStateResponseFactory = context =>
        new BadRequestObjectResult(ErrorResponse.BadRequest("One or more validation errors occurred.")));
builder.Services.AddHealthChecks();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton<RateLimiter>();

var app = builder.Build();
app.Lifetime.ApplicationStopping.Register(CustomLogger.Shutdown);

app.UseMiddleware<ExceptionHandlingMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger(options => options.RouteTemplate = "api-docs/{documentName}.json");
    app.UseSwaggerUI(options =>
    {
        options.RoutePrefix = "docs";
        options.SwaggerEndpoint("/api-docs/v1.json", "C# REST API Template v1");
    });
    app.MapGet("/api-docs", () => Results.Redirect("/api-docs/v1.json"));
}

app.UseRouting();
app.UseMiddleware<RateLimitMiddleware>();
app.UseAuthorization();

app.MapControllers();
app.MapGet("/health", async (HealthCheckService healthChecks) =>
{
    var result = await healthChecks.CheckHealthAsync();
    return Results.Json(new { status = result.Status.ToString().ToLowerInvariant() });
});

app.Run();

public partial class Program;
