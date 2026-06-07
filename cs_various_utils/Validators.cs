// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
//
// Validator methods file
//
// This module defines several methods to validate emails, passwords, tokens,
// UUIDs, URLs, and phone numbers.
//
// Required NuGet package (phone validation only):
// - libphonenumber-csharp (PhoneNumbers)
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using PhoneNumbers;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    /// <summary>
    /// Raised when a validation check fails. Map to HTTP 400 in ASP.NET middleware.
    /// </summary>
    public class ValidationException : Exception
    {
        public int StatusCode { get; }

        public ValidationException(int statusCode, string detail)
            : base(detail)
        {
            StatusCode = statusCode;
        }
    }

    public static class Validators
    {
        private static readonly Regex LocalPartRegex = new(@"^[\w\.-]+$", RegexOptions.Compiled);
        private static readonly Regex JwtRegex = new(
            @"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$",
            RegexOptions.Compiled
        );
        private static readonly Regex UuidRegex = new(
            @"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
            RegexOptions.Compiled | RegexOptions.IgnoreCase
        );

        private static readonly PhoneNumberUtil PhoneUtil = PhoneNumberUtil.GetInstance();

        /// <summary>
        /// Allowed email providers (domain part before the TLD).
        /// Configure via <see cref="SetEmailValidationConfig"/> before validating.
        /// </summary>
        public static HashSet<string> AllowedEmailProviders { get; private set; } = new(StringComparer.OrdinalIgnoreCase);

        /// <summary>
        /// Allowed email TLDs (e.g. com, org).
        /// Configure via <see cref="SetEmailValidationConfig"/> before validating.
        /// </summary>
        public static HashSet<string> AllowedEmailTlds { get; private set; } = new(StringComparer.OrdinalIgnoreCase);

        public static void SetEmailValidationConfig(
            IEnumerable<string>? allowedProviders = null,
            IEnumerable<string>? allowedTlds = null
            )
        {
            if (allowedProviders != null)
            {
                AllowedEmailProviders = new HashSet<string>(allowedProviders, StringComparer.OrdinalIgnoreCase);
            }

            if (allowedTlds != null)
            {
                AllowedEmailTlds = new HashSet<string>(allowedTlds, StringComparer.OrdinalIgnoreCase);
            }
        }

        /// <summary>
        /// Validate an email address (local_part@provider.tld).
        /// Raises <see cref="ValidationException"/> when invalid.
        /// </summary>
        public static void ValidateEmailFormat(
            string email
            )
        {
            if (email.Count(c => c == '@') != 1)
            {
                var message = $"Invalid email '{email}': must contain exactly one '@'";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            var atIndex = email.LastIndexOf('@');
            var localPart = email[..atIndex];
            var domainPart = email[(atIndex + 1)..];

            if (string.IsNullOrEmpty(localPart) || !LocalPartRegex.IsMatch(localPart))
            {
                var message = $"Invalid email '{email}': local part is invalid";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (domainPart.Count(c => c == '.') != 1)
            {
                var message = $"Invalid email '{email}': domain part must contain exactly one '.'";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            var dotIndex = domainPart.LastIndexOf('.');
            var provider = domainPart[..dotIndex];
            var tld = domainPart[(dotIndex + 1)..];

            if (!AllowedEmailProviders.Contains(provider))
            {
                var message = $"Invalid email '{email}': provider '{provider}' not allowed";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (!AllowedEmailTlds.Contains(tld))
            {
                var message = $"Invalid email '{email}': TLD '{tld}' not allowed";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            CustomLogger.Debug($"Email '{email}' is valid, proceeding");
        }

        /// <summary>
        /// Validate a password (length, case, digit, special symbol).
        /// Raises <see cref="ValidationException"/> when invalid.
        /// </summary>
        public static void ValidatePasswordFormat(
            string password
            )
        {
            if (password.Length < 8)
            {
                const string message = "Password length is too short.";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (!Regex.IsMatch(password, @"[a-z]"))
            {
                const string message = "Password validation failed: no lowercase letter found";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (!Regex.IsMatch(password, @"[A-Z]"))
            {
                const string message = "Password validation failed: no uppercase letter found";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (!Regex.IsMatch(password, @"\d"))
            {
                const string message = "Password validation failed: no digit found";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            if (!Regex.IsMatch(password, @"[^\w\s]"))
            {
                const string message = "Password validation failed: no special symbol found";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            CustomLogger.Info("Password is valid");
        }

        public static void ValidateAccessTokenFormat(
            string token
            )
        {
            if (!JwtRegex.IsMatch(token))
                throw new ValidationException(400, "Access token format is invalid.");
        }

        public static void ValidateRefreshTokenFormat(
            string token
            )
        {
            if (string.IsNullOrEmpty(token) || token.Length < 10 || !Regex.IsMatch(token, @"^[A-Za-z0-9]+$"))
                throw new ValidationException(400, "Refresh token format is invalid.");
        }

        public static void ValidateUuidFormat(
            string uuidStr
            )
        {
            if (!UuidRegex.IsMatch(uuidStr.ToLowerInvariant()))
                throw new ValidationException(400, "User ID format is invalid.");
        }

        public static bool IsUrl(
            string value
            )
        {
            return value.StartsWith("http://", StringComparison.OrdinalIgnoreCase)
                || value.StartsWith("https://", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Validate a phone number in international E.164 format (e.g. +14155552671).
        /// Raises <see cref="ValidationException"/> when invalid.
        /// </summary>
        public static void ValidatePhoneFormat(
            string phone
            )
        {
            if (string.IsNullOrWhiteSpace(phone))
            {
                const string message = "Invalid phone number: value is empty";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            var trimmed = phone.Trim();
            if (!trimmed.StartsWith('+'))
            {
                var message =
                    $"Invalid phone number '{phone}': must be in international E.164 " +
                    $"format with a leading '+' and country code (e.g. +14155552671)";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            try
            {
                var parsed = PhoneUtil.Parse(trimmed, null);
                if (!PhoneUtil.IsValidNumber(parsed))
                {
                    var message = $"Invalid phone number '{phone}': not a valid number for its country";
                    CustomLogger.Warning(message);
                    throw new ValidationException(400, message);
                }
            }
            catch (NumberParseException)
            {
                var message = $"Invalid phone number '{phone}': could not be parsed";
                CustomLogger.Warning(message);
                throw new ValidationException(400, message);
            }

            CustomLogger.Debug($"Phone '{phone}' is valid, proceeding");
        }
    }
}
