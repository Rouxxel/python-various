namespace Template.RestApi.Errors;

public sealed record ErrorResponse(int Status, string Error, string Detail)
{
    public static ErrorResponse BadRequest(string detail) => new(400, "bad_request", detail);

    public static ErrorResponse NotFound(string detail) => new(404, "not_found", detail);

    public static ErrorResponse TooManyRequests(string detail) => new(429, "rate_limit_exceeded", detail);

    public static ErrorResponse InternalServerError() =>
        new(500, "internal_server_error", "An unexpected error occurred.");
}
