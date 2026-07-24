# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY RestApiTemplate.sln ./
COPY src/RestApiTemplate/RestApiTemplate.csproj src/RestApiTemplate/
COPY tests/RestApiTemplate.Tests/RestApiTemplate.Tests.csproj tests/RestApiTemplate.Tests/
RUN dotnet restore RestApiTemplate.sln

COPY src/ src/
COPY tests/ tests/
RUN dotnet test RestApiTemplate.sln --no-restore --configuration Release
RUN dotnet publish src/RestApiTemplate/RestApiTemplate.csproj --no-restore --configuration Release --output /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home appuser

COPY --from=build /app/publish ./
RUN mkdir /app/logs && chown -R appuser:appgroup /app
USER appuser

ENV ASPNETCORE_ENVIRONMENT=Production
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail --silent http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "RestApiTemplate.dll"]
