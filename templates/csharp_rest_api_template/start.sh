#!/usr/bin/env sh
set -eu

mode="${1:-dev}"
case "$mode" in
  dev) dotnet run --project src/RestApiTemplate ;;
  release) dotnet publish src/RestApiTemplate --configuration Release --output ./publish ;;
  test) dotnet test RestApiTemplate.sln ;;
  docker) docker compose up --build ;;
  *) echo "Usage: ./start.sh [dev|release|test|docker]" >&2; exit 2 ;;
esac
