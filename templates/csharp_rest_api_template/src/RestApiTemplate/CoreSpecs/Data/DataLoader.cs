using System.Text.Json;
using System.Text.Json.Serialization;

namespace Template.RestApi.CoreSpecs.Data;

public sealed record GeneralData(
    [property: JsonPropertyName("metadata")] GeneralDataMetadata Metadata,
    [property: JsonPropertyName("languages")] IReadOnlyList<string> Languages);

public sealed record GeneralDataMetadata(
    [property: JsonPropertyName("maintainer")] string Maintainer);

/// <summary>Loads static, non-environment-specific reference data once at startup.</summary>
public sealed class DataLoader
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private DataLoader(GeneralData data) => Data = data;

    public GeneralData Data { get; }

    public static DataLoader Load(string path)
    {
        var fullPath = Path.GetFullPath(path);
        if (!File.Exists(fullPath))
        {
            throw new FileNotFoundException(
                $"CoreSpecs static-data file was not found: '{fullPath}'.", fullPath);
        }

        try
        {
            var data = JsonSerializer.Deserialize<GeneralData>(File.ReadAllText(fullPath), JsonOptions)
                ?? throw new InvalidOperationException($"CoreSpecs static-data file '{fullPath}' is empty.");
            if (string.IsNullOrWhiteSpace(data.Metadata.Maintainer) || data.Languages.Count == 0)
            {
                throw new InvalidOperationException(
                    $"CoreSpecs static-data file '{fullPath}' is missing required values.");
            }

            return new DataLoader(data);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"CoreSpecs static-data file '{fullPath}' contains invalid JSON.", exception);
        }
    }

    public IReadOnlyList<string> GetLanguages() => Data.Languages;
}
