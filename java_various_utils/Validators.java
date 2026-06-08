// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Validator methods file
//
// Defines several methods to validate emails, passwords, tokens, UUIDs, URLs,
// and phone numbers. Validation failures throw a ValidationException carrying an
// HTTP-style status code (map it to a 400 response in your web framework).
//
// Depends on the sibling CustomLogger util (for warning/debug logging).
//
// Required dependency (phone validation only):
// - libphonenumber  (Maven: com.googlecode.libphonenumber:libphonenumber)
//   If you don't need validatePhoneFormat, you can delete that method and the
//   PhoneNumberUtil import to drop the dependency entirely.
//
// HOW TO TEST (standalone)
//   javac CustomLogger.java Validators.java   # plus libphonenumber on the classpath
//   java -cp ".;libphonenumber.jar" java_various_utils.Validators   (use ':' on Linux/macOS)

// Change package based on whatever project is implemented
package java_various_utils;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Pattern;

import com.google.i18n.phonenumbers.NumberParseException;
import com.google.i18n.phonenumbers.PhoneNumberUtil;
import com.google.i18n.phonenumbers.Phonenumber.PhoneNumber;

public final class Validators {

    /**
     * Raised when a validation check fails. Map StatusCode to HTTP 400 in middleware.
     */
    public static class ValidationException extends RuntimeException {
        private final int statusCode;

        public ValidationException(int statusCode, String detail) {
            super(detail);
            this.statusCode = statusCode;
        }

        public int getStatusCode() {
            return statusCode;
        }
    }

    private static final Pattern LOCAL_PART_REGEX = Pattern.compile("^[\\w.-]+$");
    private static final Pattern JWT_REGEX =
            Pattern.compile("^[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+$");
    private static final Pattern UUID_REGEX = Pattern.compile(
            "^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$");
    private static final Pattern REFRESH_TOKEN_REGEX = Pattern.compile("^[A-Za-z0-9]+$");

    private static final PhoneNumberUtil PHONE_UTIL = PhoneNumberUtil.getInstance();

    // Allowed email providers (domain part before the TLD) and TLDs.
    // Configure via setEmailValidationConfig before validating.
    private static Set<String> allowedEmailProviders = caseInsensitiveSet();
    private static Set<String> allowedEmailTlds = caseInsensitiveSet();

    private Validators() { }

    private static Set<String> caseInsensitiveSet() {
        return new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
    }

    public static void setEmailValidationConfig(Collection<String> allowedProviders,
                                               Collection<String> allowedTlds) {
        if (allowedProviders != null) {
            Set<String> providers = caseInsensitiveSet();
            providers.addAll(allowedProviders);
            allowedEmailProviders = providers;
        }
        if (allowedTlds != null) {
            Set<String> tlds = caseInsensitiveSet();
            tlds.addAll(allowedTlds);
            allowedEmailTlds = tlds;
        }
    }

    /**
     * Validate an email address (local_part@provider.tld).
     * Throws ValidationException when invalid.
     */
    public static void validateEmailFormat(String email) {
        if (countChar(email, '@') != 1) {
            String message = "Invalid email '" + email + "': must contain exactly one '@'";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        int atIndex = email.lastIndexOf('@');
        String localPart = email.substring(0, atIndex);
        String domainPart = email.substring(atIndex + 1);

        if (localPart.isEmpty() || !LOCAL_PART_REGEX.matcher(localPart).matches()) {
            String message = "Invalid email '" + email + "': local part is invalid";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        if (countChar(domainPart, '.') != 1) {
            String message = "Invalid email '" + email + "': domain part must contain exactly one '.'";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        int dotIndex = domainPart.lastIndexOf('.');
        String provider = domainPart.substring(0, dotIndex);
        String tld = domainPart.substring(dotIndex + 1);

        if (!allowedEmailProviders.contains(provider)) {
            String message = "Invalid email '" + email + "': provider '" + provider + "' not allowed";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        if (!allowedEmailTlds.contains(tld)) {
            String message = "Invalid email '" + email + "': TLD '" + tld + "' not allowed";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        CustomLogger.debug("Email '" + email + "' is valid, proceeding");
    }

    /**
     * Validate a password (length, case, digit, special symbol).
     * Throws ValidationException when invalid.
     */
    public static void validatePasswordFormat(String password) {
        if (password.length() < 8) {
            String message = "Password length is too short.";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }
        if (!Pattern.compile("[a-z]").matcher(password).find()) {
            String message = "Password validation failed: no lowercase letter found";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }
        if (!Pattern.compile("[A-Z]").matcher(password).find()) {
            String message = "Password validation failed: no uppercase letter found";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }
        if (!Pattern.compile("\\d").matcher(password).find()) {
            String message = "Password validation failed: no digit found";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }
        if (!Pattern.compile("[^\\w\\s]").matcher(password).find()) {
            String message = "Password validation failed: no special symbol found";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }
        CustomLogger.info("Password is valid");
    }

    public static void validateAccessTokenFormat(String token) {
        if (token == null || !JWT_REGEX.matcher(token).matches()) {
            throw new ValidationException(400, "Access token format is invalid.");
        }
    }

    public static void validateRefreshTokenFormat(String token) {
        if (token == null || token.length() < 10 || !REFRESH_TOKEN_REGEX.matcher(token).matches()) {
            throw new ValidationException(400, "Refresh token format is invalid.");
        }
    }

    public static void validateUuidFormat(String uuidStr) {
        if (uuidStr == null || !UUID_REGEX.matcher(uuidStr.toLowerCase()).matches()) { // RFC 4122
            throw new ValidationException(400, "User ID format is invalid.");
        }
    }

    public static boolean isUrl(String value) {
        if (value == null) return false;
        String lower = value.toLowerCase();
        return lower.startsWith("http://") || lower.startsWith("https://");
    }

    /**
     * Validate a phone number in international E.164 format (e.g. +14155552671).
     * Region-agnostic: the leading '+' and country code identify the country.
     * Throws ValidationException when invalid.
     */
    public static void validatePhoneFormat(String phone) {
        if (phone == null || phone.trim().isEmpty()) {
            String message = "Invalid phone number: value is empty";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        String trimmed = phone.trim();
        if (!trimmed.startsWith("+")) {
            String message = "Invalid phone number '" + phone + "': must be in international E.164 "
                    + "format with a leading '+' and country code (e.g. +14155552671)";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        try {
            // null default region; the '+' country code identifies the country
            PhoneNumber parsed = PHONE_UTIL.parse(trimmed, null);
            if (!PHONE_UTIL.isValidNumber(parsed)) {
                String message = "Invalid phone number '" + phone + "': not a valid number for its country";
                CustomLogger.warning(message);
                throw new ValidationException(400, message);
            }
        } catch (NumberParseException e) {
            String message = "Invalid phone number '" + phone + "': could not be parsed";
            CustomLogger.warning(message);
            throw new ValidationException(400, message);
        }

        CustomLogger.debug("Phone '" + phone + "' is valid, proceeding");
    }

    private static int countChar(String s, char c) {
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == c) count++;
        }
        return count;
    }

    // Standalone smoke test.
    public static void main(String[] args) {
        CustomLogger.setup("logs", "validators_test", CustomLogger.LogLevel.DEBUG);
        setEmailValidationConfig(new HashSet<>(java.util.Arrays.asList("gmail", "outlook")),
                new HashSet<>(java.util.Arrays.asList("com", "org")));

        try {
            validateEmailFormat("ada@gmail.com");
            System.out.println("email OK");
        } catch (ValidationException e) {
            System.out.println("email rejected: " + e.getMessage());
        }

        try {
            validatePasswordFormat("Str0ng!Pass");
            System.out.println("password OK");
        } catch (ValidationException e) {
            System.out.println("password rejected: " + e.getMessage());
        }

        System.out.println("isUrl('https://x.com') = " + isUrl("https://x.com"));
        CustomLogger.shutdown();
    }
}
