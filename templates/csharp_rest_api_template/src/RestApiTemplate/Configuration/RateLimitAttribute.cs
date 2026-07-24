namespace Template.RestApi.Configuration;

[AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = true)]
public sealed class RateLimitAttribute(string endpointKey) : Attribute
{
    public string EndpointKey { get; } = endpointKey;
}
