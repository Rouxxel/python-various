namespace Template.RestApi.Errors;

public sealed class RateLimitExceededException(string message) : Exception(message);
