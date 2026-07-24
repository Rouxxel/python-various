using System.Text.Json.Serialization;

namespace Template.RestApi.CoreSpecs.Configuration;

public sealed record CoreSpecsConfiguration(
    [property: JsonPropertyName("defaults")] DefaultsConfiguration Defaults,
    [property: JsonPropertyName("logging")] LoggingConfiguration Logging,
    [property: JsonPropertyName("email_validation")] EmailValidationConfiguration EmailValidation,
    [property: JsonPropertyName("network")] NetworkConfiguration Network,
    [property: JsonPropertyName("endpoints")] IReadOnlyDictionary<string, EndpointSpecification> Endpoints);

public sealed record DefaultsConfiguration(
    [property: JsonPropertyName("general_data_path")] string GeneralDataPath);

public sealed record LoggingConfiguration(
    [property: JsonPropertyName("logging_level")] string LoggingLevel,
    [property: JsonPropertyName("dir_name")] string DirectoryName,
    [property: JsonPropertyName("log_file_name")] string LogFileName);

public sealed record EmailValidationConfiguration(
    [property: JsonPropertyName("allowed_providers")] IReadOnlyList<string> AllowedProviders,
    [property: JsonPropertyName("allowed_tlds")] IReadOnlyList<string> AllowedTlds);

public sealed record NetworkConfiguration(
    [property: JsonPropertyName("server_port")] int ServerPort,
    [property: JsonPropertyName("host")] string Host,
    [property: JsonPropertyName("context_path")] string ContextPath);

public sealed record EndpointSpecification(
    [property: JsonPropertyName("request_limit")] int RequestLimit,
    [property: JsonPropertyName("unit_of_time_for_limit")] string UnitOfTimeForLimit,
    [property: JsonPropertyName("endpoint_prefix")] string EndpointPrefix,
    [property: JsonPropertyName("endpoint_tag")] string EndpointTag,
    [property: JsonPropertyName("endpoint_route")] string EndpointRoute);
