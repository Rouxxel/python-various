namespace Template.RestApi.Errors;

public sealed class ResourceNotFoundException(string message) : KeyNotFoundException(message);
