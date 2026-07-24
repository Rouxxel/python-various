param(
    [ValidateSet("dev", "release", "test", "docker")]
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
switch ($Mode) {
    "dev" { dotnet run --project src/RestApiTemplate }
    "release" { dotnet publish src/RestApiTemplate --configuration Release --output ./publish }
    "test" { dotnet test RestApiTemplate.sln }
    "docker" { docker compose up --build }
}
