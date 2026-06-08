// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Recursively scans a project starting from a resolved root directory and deletes
// target folders matching the specified names (e.g. "__pycache__", "logs", "bin",
// "obj", "build", "dist").
//
// HOW IT WORKS
//   1. Directory climbing: starting from a given path, climbs up parent directories
//      until it finds a folder whose name matches ROOT_FOLDER (case-insensitive).
//      This keeps the cleanup confined to the project root and prevents leaking out
//      into outer folders (like C:\ or the user directory).
//   2. Recursive traversal: from that matched root, walks downward and deletes any
//      directory whose name matches one of FOLDERS_TO_REMOVE (children before parents).
//
// No external dependencies (pure JDK).
//
// HOW TO TEST (standalone)
//   javac LogsDeleter.java
//   java LogsDeleter
//   -> climbs up from the working directory to the folder named ROOT_FOLDER and
//      deletes the configured target folders. Edit ROOT_FOLDER before running.

// Change package based on whatever project is implemented
package java_various_utils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public final class LogsDeleter {

    // FORCE USER TO SET THE ROOT FOLDER NAME (case-insensitive),
    // e.g. "drone_battery_performance_prediction"
    public static final String ROOT_FOLDER = "python-various";
    public static final String[] FOLDERS_TO_REMOVE =
            { "__pycache__", "logs", ".pytest_cache", "build", "dist", "bin", "obj" };

    private LogsDeleter() { }

    /**
     * Climbs up directories starting from startPath until it finds a directory
     * whose folder name matches targetName (case-insensitive).
     */
    public static Path findProjectRootByName(String startPath, String targetName) {
        Path current = Paths.get(startPath).toAbsolutePath().normalize();
        if (Files.isRegularFile(current)) {
            current = current.getParent();
        }

        String targetLower = targetName.trim().toLowerCase();
        while (current != null) {
            Path name = current.getFileName();
            if (name != null && name.toString().toLowerCase().equals(targetLower)) {
                return current;
            }
            Path parent = current.getParent();
            if (parent == null || parent.equals(current)) { // reached filesystem root
                break;
            }
            current = parent;
        }

        throw new RuntimeException("Could not find any parent directory named '"
                + targetName + "' starting from '"
                + Paths.get(startPath).toAbsolutePath().normalize() + "'.");
    }

    /**
     * Removes folders matching foldersToRemove from rootDir and all its subdirectories.
     */
    public static void removeFolders(Path rootDir, String[] foldersToRemove) {
        if (!Files.exists(rootDir)) {
            throw new RuntimeException("The specified root directory does not exist: " + rootDir);
        }

        List<String> targets = (foldersToRemove == null || foldersToRemove.length == 0)
                ? Arrays.asList("__pycache__", "logs")
                : Arrays.asList(foldersToRemove);

        List<Path> matches;
        try (Stream<Path> walk = Files.walk(rootDir)) {
            matches = walk
                    .filter(Files::isDirectory)
                    .filter(p -> {
                        Path name = p.getFileName();
                        return name != null && targets.stream()
                                .anyMatch(t -> t.equalsIgnoreCase(name.toString()));
                    })
                    // Delete deepest paths first so nested targets go before their parents
                    .sorted(Comparator.comparingInt(LogsDeleter::depth).reversed())
                    .collect(Collectors.toList());
        } catch (IOException e) {
            System.out.println("Failed to scan " + rootDir + ": " + e.getMessage());
            return;
        }

        for (Path dir : matches) {
            try {
                deleteRecursively(dir);
                System.out.println("Deleted: " + dir);
            } catch (IOException e) {
                System.out.println("Failed to delete " + dir + ": " + e.getMessage());
            }
        }
    }

    private static int depth(Path p) {
        return p.getNameCount();
    }

    private static void deleteRecursively(Path dir) throws IOException {
        try (Stream<Path> walk = Files.walk(dir)) {
            walk.sorted(Comparator.reverseOrder())
                .forEach(p -> {
                    try {
                        Files.delete(p);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });
        } catch (RuntimeException e) {
            if (e.getCause() instanceof IOException) throw (IOException) e.getCause();
            throw e;
        }
    }

    // Main execution entry point.
    public static void main(String[] args) {
        if (ROOT_FOLDER == null || ROOT_FOLDER.isEmpty()) {
            System.out.println("Error: ROOT_FOLDER is not set! Please open this file and specify "
                    + "your project's root folder name in the 'ROOT_FOLDER' constant.");
            return;
        }

        String startPath = System.getProperty("user.dir");
        Path actualRoot = findProjectRootByName(startPath, ROOT_FOLDER);
        System.out.println("Project root found at: " + actualRoot);
        removeFolders(actualRoot, FOLDERS_TO_REMOVE);
    }
}
