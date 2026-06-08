// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Increase video resolution using ffmpeg and the Lanczos algorithm.
//
// Provides two main methods:
//   1. upscaleVideoLanczos: Doubles the resolution (or by a specified scale factor).
//   2. scaleToResolution:   Scales the video to a specific resolution (e.g. 1920x1080).
//
// Requirements:
// - ffmpeg must be installed and available on the system PATH.
//   (No external Java libraries are required - this shells out to the ffmpeg CLI.)
//
// HOW TO TEST (standalone)
//   javac FfmpegVideoResolutionIncreaser.java
//   java FfmpegVideoResolutionIncreaser
//   -> reads "old_vid.mp4" in the working directory and writes "upscaled_video.mp4".

// Change package based on whatever project is implemented
package java_various_utils;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

public final class FfmpegVideoResolutionIncreaser {

    private FfmpegVideoResolutionIncreaser() { }

    /**
     * Doubles the resolution (or by scaleFactor) using the Lanczos algorithm.
     */
    public static void upscaleVideoLanczos(String inputFile, String outputFile, int scaleFactor) {
        // scale=iw*2:ih*2 multiplies input width and height by 2
        List<String> cmd = Arrays.asList(
                "ffmpeg", "-i", inputFile,
                "-vf", "scale=iw*" + scaleFactor + ":ih*" + scaleFactor + ":flags=lanczos",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                outputFile
        );

        runFfmpeg(cmd, "Success! Scaled video saved to: " + outputFile);
    }

    /**
     * Scales a video to a specific resolution using the Lanczos algorithm.
     */
    public static void scaleToResolution(String inputFile, String outputFile, int width, int height) {
        List<String> cmd = Arrays.asList(
                "ffmpeg", "-i", inputFile,
                "-vf", "scale=" + width + ":" + height + ":flags=lanczos",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                outputFile
        );

        runFfmpeg(cmd, "Success! Video scaled to " + width + "x" + height + " saved to: " + outputFile);
    }

    private static void runFfmpeg(List<String> cmd, String successMessage) {
        try {
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.inheritIO(); // forward ffmpeg's stdout/stderr to the console
            Process process = pb.start();
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                System.out.println(successMessage);
            } else {
                System.out.println("An error occurred: ffmpeg exited with code " + exitCode);
            }
        } catch (IOException e) {
            System.out.println("An error occurred: " + e.getMessage()
                    + " (is ffmpeg installed and on your PATH?)");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.out.println("An error occurred: process was interrupted.");
        }
    }

    // --- Example usage / standalone test ---
    public static void main(String[] args) {
        String inputPath = "old_vid.mp4";   // Ensure this file exists in your folder
        String outputFile = "upscaled_video.mp4";

        // 1. Double the resolution
        upscaleVideoLanczos(inputPath, outputFile, 2);

        // 2. Scale to 1080p
        // scaleToResolution(inputPath, outputFile, 1920, 1080);
    }
}
