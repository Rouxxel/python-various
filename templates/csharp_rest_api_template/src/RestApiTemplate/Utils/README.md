# Template utility integration

The following files are copied and namespace-adapted from the repository's
`cs_various_utils/` folder: `CustomLogger`, `Validators`, `SecureFileIo`,
`KeysGenerator`, and `LogsDeleter`.

`UtilityStartup` configures logging, email validation, and the allowed file-I/O
root from `Resources/CoreSpecs/Configuration/config_file.json` during startup.
`SecureFileIo` supports YAML only when the consuming project explicitly adds
`YamlDotNet`; it is intentionally not a required dependency for this template.

No `EnDeCrypt.cs` counterpart currently exists in `cs_various_utils`. RSA key
generation is available through `KeysGenerator`, but encrypted request fields
are intentionally opt-in: add a reviewed RSA OAEP-SHA256 helper only when an
API contract requires it.

After the ASP.NET Core 8 runtime is installed, generate development keys with:

```powershell
dotnet run --project src/RestApiTemplate -- --generate-rsa-keys
```

The generated PEM files are ignored by Git. Do not use this command to create
or store production secrets on a developer workstation.
