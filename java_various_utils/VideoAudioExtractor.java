// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Extract audio and video from a given video file.
//
// Separates the audio and (audio-less) video components of a video file. The
// Python original used moviepy; this Java version shells out to the ffmpeg CLI,
// which keeps it dependency-free and handles every container/codec ffmpeg knows.
//
// Requirements:
// - ffmpeg must be installed and available on the system PATH.
//   (No external Java libraries are required.)
//
// HOW TO TEST (standalone)
//   javac VideoAudioExtractor.java
//   java VideoAudioExtractor
//   -> reads the configured input video and writes "<name>_audio.<fmt>" and
//      "<name>_no_audio.<fmt>" next to it. Edit the input path in main() first.

// Change package based on whatever project is implemented
package java_various_utils;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public final class VideoAudioExtractor {

    private VideoAudioExtractor() { }

    /**
     * Extract audio from a given video file. The output is saved next to the input.
     */
    public static void extractAudio(String inputPath, String outputAudioFormat) {
        if (inputPath == null || !new File(inputPath).exists()) {
            System.out.println("Error: File not found.");
            return;
        }

        String baseStr = stripExtension(inputPath);
        String output = baseStr + "_audio." + outputAudioFormat;
        System.out.println("--- Processing: " + new File(inputPath).getName() + " Audio extraction ---");
        System.out.println("Extracting audio to " + output + "...");

        // -vn: drop video stream, keep audio only
        List<String> cmd = Arrays.asList("ffmpeg", "-y", "-i", inputPath, "-vn", output);
        if (runFfmpeg(cmd)) {
            System.out.println("Success, audio file has been saved as " + new File(output).getAbsolutePath());
        }
    }

    /**
     * Extract video (without audio) from a given video file. Saved next to the input.
     */
    public static void extractVideo(String inputPath, String outputVideoFormat) {
        if (inputPath == null || !new File(inputPath).exists()) {
            System.out.println("Error: video input file not found.");
            return;
        }

        String baseStr = stripExtension(inputPath);
        String output = baseStr + "_no_audio." + outputVideoFormat;
        System.out.println("--- Processing: " + new File(inputPath).getName() + " video extraction ---");
        System.out.println("Exporting video to " + output + "...");

        // -an: drop audio stream; -c:v copy keeps the original video codec (fast, lossless)
        List<String> cmd = Arrays.asList("ffmpeg", "-y", "-i", inputPath, "-an", "-c:v", "copy", output);
        if (runFfmpeg(cmd)) {
            System.out.println("Success, video file has been saved as " + new File(output).getAbsolutePath());
        }
    }

    /**
     * Run audio and video extraction in parallel using separate threads.
     */
    public static void parallelExtraction(String inputPath,
                                          boolean extractAudio, String outputAudioFormat,
                                          boolean extractVideo, String outputVideoFormat) {
        CompletableFuture<Void> audioFuture = CompletableFuture.completedFuture(null);
        CompletableFuture<Void> videoFuture = CompletableFuture.completedFuture(null);

        if (extractAudio && outputAudioFormat != null) {
            audioFuture = CompletableFuture.runAsync(() -> extractAudio(inputPath, outputAudioFormat));
        }
        if (extractVideo && outputVideoFormat != null) {
            videoFuture = CompletableFuture.runAsync(() -> extractVideo(inputPath, outputVideoFormat));
        }

        CompletableFuture.allOf(audioFuture, videoFuture).join();
        System.out.println("--- Task/s completed! ---");
    }

    private static boolean runFfmpeg(List<String> cmd) {
        try {
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.inheritIO();
            Process process = pb.start();
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                System.out.println("ffmpeg failed with exit code " + exitCode + ".");
                return false;
            }
            return true;
        } catch (IOException e) {
            System.out.println("An error occurred: " + e.getMessage()
                    + " (is ffmpeg installed and on your PATH?)");
            return false;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.out.println("An error occurred: process was interrupted.");
            return false;
        }
    }

    private static String stripExtension(String path) {
        int dot = path.lastIndexOf('.');
        int sep = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'));
        return dot > sep ? path.substring(0, dot) : path;
    }

    // Main execution entry point - can be adapted to command-line
    // arguments or hardcoded values for testing.
    public static void main(String[] args) {
        String inputPath = "old_video.mp4";
        String audioFormat = "mp3";
        String videoFormat = "mp4";

        // For parallel execution of both tasks:
        parallelExtraction(inputPath, true, audioFormat, true, videoFormat);

        // Or run sequentially:
        // extractAudio(inputPath, audioFormat);
        // extractVideo(inputPath, videoFormat);
    }
}
