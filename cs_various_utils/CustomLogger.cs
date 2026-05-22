// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
using System;
using System.IO;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    // Custom level mapping
    public enum LogLevel
    {
        Debug = 0,
        Info = 1,
        Warning = 2,
        Error = 3,
        Critical = 4
    }

    public static class CustomLogger
    {
        // Internal state for log file management
        private static readonly object _lock = new object();
        private static StreamWriter _fileWriter;
        private static bool _isInitialized;
        private static string _currentLogDate;
        private static string _currentLogFile;

        // Default configuration values - 
        // can be overridden in Setup() or 
        // directly here before initialization
        public static string LogDirectory = "logs";
        public static string LogFileName = "log_file_name_should_come_from_a_config_file_in_lower_case";
        public static LogLevel MinimumLogLevel = LogLevel.Debug; // Configurable log level filtering

        public static void Setup(
            string logDirectory = null, 
            string logFileName = null, 
            LogLevel minLogLevel = LogLevel.Debug
            ){
            lock (_lock)
            {
                try
                {
                    if (!string.IsNullOrEmpty(logDirectory)) LogDirectory = logDirectory;
                    if (!string.IsNullOrEmpty(logFileName)) LogFileName = logFileName;
                    MinimumLogLevel = minLogLevel;

                    Directory.CreateDirectory(LogDirectory);
                    
                    // Initialize the log file for today
                    _currentLogDate = DateTime.UtcNow.ToString("yyyyMMdd");
                    var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
                    _currentLogFile = Path.Combine(LogDirectory, $"{LogFileName}_{timestamp}.log");
                    
                    OpenLogFile(_currentLogFile);
                    _isInitialized = true;
                    
                    Info("PROJECTNAME backend server starting");
                    Warning($"Current working directory: {Directory.GetCurrentDirectory()}, Logs written to '{LogDirectory}'");
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Failed to initialize logger: {ex.Message}");
                    _isInitialized = false;
                }
            }
        }

        private static void OpenLogFile(
            string filePath
            ){
            try
            {
                // Close existing writer if any
                _fileWriter?.Dispose();
                
                _fileWriter = new StreamWriter(
                    new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.Read))
                {
                    AutoFlush = true
                };
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Failed to open log file '{filePath}': {ex.Message}");
                _fileWriter = null;
            }
        }

        private static void CheckRotation(
        ){
            // Check if date has changed for daily log rotation
            string todayDate = DateTime.UtcNow.ToString("yyyyMMdd");
            if (todayDate != _currentLogDate)
            {
                var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
                var newLogFile = Path.Combine(LogDirectory, $"{LogFileName}_{timestamp}.log");
                OpenLogFile(newLogFile);
                _currentLogDate = todayDate;
                _currentLogFile = newLogFile;
            }
        }

        private static void Write(
            LogLevel level, 
            string message
            ){
            // Filter by log level
            if (level < MinimumLogLevel)
                return;

            if (!_isInitialized)
            {
                Console.Error.WriteLine($"WARNING: Logger not initialized. Call Setup() before logging. Message: {message}");
                return;
            }

            try
            {
                lock (_lock)
                {
                    CheckRotation();
                    
                    var ts = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss.fff");
                    var levelStr = level.ToString().ToUpper();
                    var line = $"[{ts}] [{levelStr}] {message}";
                    
                    Console.WriteLine(line);
                    
                    if (_fileWriter != null)
                    {
                        _fileWriter.WriteLine(line);
                    }
                }
            }
            catch (Exception ex)
            {
                // Fail gracefully - log to console only if file write fails
                Console.Error.WriteLine($"Error writing to log: {ex.Message}");
                Console.Error.WriteLine($"Original message: {message}");
            }
        }

        //Actual logging methods for each level - can be 
        //extended with additional parameters as needed
        public static void Debug(string message) => Write(LogLevel.Debug, message);
        public static void Info(string message) => Write(LogLevel.Info, message);
        public static void Warning(string message) => Write(LogLevel.Warning, message);
        public static void Error(string message) => Write(LogLevel.Error, message);
        public static void Critical(string message) => Write(LogLevel.Critical, message);

        // Properly closes and disposes the file writer. 
        // Call before application shutdown.
        public static void Shutdown(
        ){
            lock (_lock)
            {
                try
                {
                    if (_fileWriter != null)
                    {
                        Info("Logger shutting down");
                        _fileWriter.Flush();
                        _fileWriter.Dispose();
                        _fileWriter = null;
                    }
                    _isInitialized = false;
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error during logger shutdown: {ex.Message}");
                }
            }
        }
    }
}

    // Example usage (copy into your project's startup or main code):
    // using cs_various_utils;
    //
    // CustomLogger.Setup("logs", "my_app_log", LogLevel.Info);
    // CustomLogger.Info("Info message");
    // CustomLogger.Debug("Debug message"); // Won't log if MinimumLogLevel is Info
    //
    // CustomLogger.Warning($"Warning message: {someValue}");
    // CustomLogger.Error($"Error message: {someValue}");
    //
    // // Shutdown before application exit:
    // CustomLogger.Shutdown();
    //
    // Notes:
    // - `Setup()` must be called before logging to initialize the log file.
    // - `MinimumLogLevel` controls which messages are written to file and console.
    // - Log rotation is handled by date changes; a new file is created when the UTC date changes.
    // - Failures writing to the log file are handled gracefully and printed to stderr.
    // - The logger is thread-safe via internal locking.
    //
    // Available Log Levels: Debug, Info, Warning, Error, Critical
