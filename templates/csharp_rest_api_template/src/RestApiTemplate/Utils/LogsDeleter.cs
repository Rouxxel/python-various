// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
using System;
using System.IO;
using System.Linq;

// Change namespace based on whatever project is implemented
namespace Template.RestApi.Utils
{
    public static class LogsDeleter
    {
        public static string FindProjectRootByName(
            string startPath,
            string? targetName = null
            ){
            var current = Path.GetFullPath(startPath);
            if (File.Exists(current)) current = Path.GetDirectoryName(current);
            var targetLower = targetName?.Trim().ToLower();
            while (!string.IsNullOrEmpty(current))
            {
                if (Path.GetFileName(current).ToLower() == targetLower) return current;
                var parent = Path.GetDirectoryName(current);
                if (string.IsNullOrEmpty(parent) || parent == current) break;
                current = parent;
            }
            throw new Exception($"Could not find a parent directory named '{targetName}' starting from '{startPath}'");
        }

        public static void RemoveLogFolders(
            string rootDir, 
            string[] foldersToRemove
            ){
            var targets = (foldersToRemove == null || foldersToRemove.Length == 0)
                ? new[] { "bin", "obj", "logs" }
                : foldersToRemove;

            if (!Directory.Exists(rootDir)) throw new Exception($"The specified root directory does not exist: {rootDir}");

            // Collect matching directories first, then delete children before parents
            var matches = Directory.EnumerateDirectories(rootDir, "*", SearchOption.AllDirectories)
                .Where(d => targets.Any(t => string.Equals(Path.GetFileName(d), t, StringComparison.OrdinalIgnoreCase)))
                .ToList();

            // Order by depth (longer paths first) so nested targets are deleted before their parents
            var ordered = matches.OrderByDescending(d => d.Count(c => c == Path.DirectorySeparatorChar));

            foreach (var dir in ordered)
            {
                try
                {
                    Directory.Delete(dir, true);
                    Console.WriteLine($"Deleted: {dir}");
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Failed to delete {dir}: {e.Message}");
                }
            }
        }

    }
}
