using System.Text.Json;
using Template.RestApi.Errors;
using Template.RestApi.Utils;

namespace Template.RestApi.Middleware;

public sealed class ExceptionHandlingMiddleware(RequestDelegate next)
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await next(context);
            if (context.Response.StatusCode == StatusCodes.Status404NotFound && !context.Response.HasStarted)
            {
                await WriteError(context, ErrorResponse.NotFound("The requested resource was not found."));
            }
        }
        catch (ValidationException exception)
        {
            await WriteError(context, ErrorResponse.BadRequest(exception.Message));
        }
        catch (RateLimitExceededException exception)
        {
            await WriteError(context, ErrorResponse.TooManyRequests(exception.Message));
        }
        catch (KeyNotFoundException exception)
        {
            await WriteError(context, ErrorResponse.NotFound(exception.Message));
        }
        catch (Exception exception)
        {
            CustomLogger.Error($"Unhandled request exception: {exception.Message}");
            await WriteError(context, ErrorResponse.InternalServerError());
        }
    }

    private static async Task WriteError(HttpContext context, ErrorResponse error)
    {
        context.Response.Clear();
        context.Response.StatusCode = error.Status;
        context.Response.ContentType = "application/json";
        await context.Response.WriteAsync(JsonSerializer.Serialize(error, JsonOptions));
    }
}
