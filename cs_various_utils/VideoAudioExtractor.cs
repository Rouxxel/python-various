// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using NAudio.Wave;
using NAudio.MediaFoundation;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public static class VideoAudioExtractor
    {
        public static void ExtractAudio(
            string inputPath, 
            string outputAudioFormat = "mp3"
            ){
            if (string.IsNullOrEmpty(inputPath) || !File.Exists(inputPath))
            {
                Console.WriteLine("Error: File not found.");
                return;
            }

            try
            {
                MediaFoundationApi.Startup();
                using var reader = new MediaFoundationReader(inputPath);
                var baseStr = Path.Combine(Path.GetDirectoryName(inputPath) ?? "", Path.GetFileNameWithoutExtension(inputPath));
                var output = $"{baseStr}_audio.{outputAudioFormat}";
                Console.WriteLine($"--- Processing: {Path.GetFileName(inputPath)} Audio extraction ---");

                var outputDirectory = Path.GetDirectoryName(output);
                if (!string.IsNullOrEmpty(outputDirectory))
                {
                    Directory.CreateDirectory(outputDirectory);
                }

                if (outputAudioFormat.Equals("wav", StringComparison.OrdinalIgnoreCase))
                {
                    WaveFileWriter.CreateWaveFile(output, reader);
                }
                else if (outputAudioFormat.Equals("mp3", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        MediaFoundationEncoder.EncodeToMp3(reader, output);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine($"MP3 encoding via MediaFoundation failed: {e.Message}");
                        Console.WriteLine("Falling back to WAV output.");
                        var wavOut = Path.ChangeExtension(output, "wav");
                        reader.Dispose();
                        using var fallbackReader = new MediaFoundationReader(inputPath);
                        WaveFileWriter.CreateWaveFile(wavOut, fallbackReader);
                        output = wavOut;
                    }
                }
                else
                {
                    Console.WriteLine($"Unsupported audio format: {outputAudioFormat}. Supported: wav, mp3");
                    return;
                }

                Console.WriteLine($"Success, Audio file has been saved as {Path.GetFullPath(output)}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"An error occurred: {e}");
            }
            finally
            {
                MediaFoundationApi.Shutdown();
            }
        }

        public static void ExtractVideoWithoutAudio(
            string inputPath,
            string outputVideoFormat
            ){
            if (string.IsNullOrEmpty(inputPath) || !File.Exists(inputPath))
            {
                Console.WriteLine("Error: video input file not found.");
                return;
            }

            var output = Path.ChangeExtension(inputPath, $"_video.{outputVideoFormat}");
            Console.WriteLine($"--- Processing: {Path.GetFileName(inputPath)} Video extraction without audio ---");
            Console.WriteLine($"Output will be: {Path.GetFullPath(output)}");

            var outputDirectory = Path.GetDirectoryName(output);
            if (!string.IsNullOrEmpty(outputDirectory))
            {
                Directory.CreateDirectory(outputDirectory);
            }

            var ffmpegExe = "ffmpeg";
            var arguments = $"-y -i \"{inputPath}\" -c:v copy -an \"{output}\"";
            var startInfo = new ProcessStartInfo
            {
                FileName = ffmpegExe,
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };

            try
            {
                using var process = Process.Start(startInfo);
                if (process == null)
                {
                    Console.WriteLine("Error: unable to start ffmpeg process.");
                    return;
                }

                var stdOut = process.StandardOutput.ReadToEnd();
                var stdErr = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (process.ExitCode != 0)
                {
                    Console.WriteLine($"ffmpeg failed with exit code {process.ExitCode}.");
                    Console.WriteLine(stdErr);
                    return;
                }

                Console.WriteLine("Success, video file has been saved as " + Path.GetFullPath(output));
            }
            catch (Exception e)
            {
                Console.WriteLine("An error occurred while extracting video without audio: " + e.Message);
            }
        }

        public static async Task ParallelExtraction(
            string inputPath, 
            bool extractAudio = true, 
            string? outputAudioFormat = null, 
            bool extractVideo = true, 
            string? outputVideoFormat = null
            ){
            var tasks = new System.Collections.Generic.List<Task>();
            if (extractAudio && !string.IsNullOrEmpty(outputAudioFormat))
            {
                tasks.Add(Task.Run(() => ExtractAudio(inputPath, outputAudioFormat)));
            }
            if (extractVideo && !string.IsNullOrEmpty(outputVideoFormat))
            {
                tasks.Add(Task.Run(() => ExtractVideoWithoutAudio(inputPath, outputVideoFormat)));
            }

            try
            {
                await Task.WhenAll(tasks);
            }
            catch (NotSupportedException e)
            {
                Console.WriteLine(e.Message);
            }

            Console.WriteLine("--- Task/s completed! ---");
        }

        //Main execution entry point - can be adapted to 
        //command-line arguments or hardcoded values for testing
        public static void Main(string[] args)
        {
            // Enable for command-line argument parsing
            //if (args.Length == 0)
            //{
            //    Console.WriteLine("Usage: VideoAudioExtractor <input_video_path> [audio_format] [video_format]");
            //    Console.WriteLine("Example: VideoAudioExtractor video.mp4 mp3");
            //    return;
            //}

            var inputPath = "../tra.mp4"; // args.Length > 3 ? args[1] : null;
            var audioFormat = "wav"; // args.Length > 1 ? args[1] : null;
            var videoFormat = "mp4"; // args.Length > 2 ? args[2] : null;

            // For parallel execution of both tasks
            //ParallelExtraction(
            //    inputPath, 
            //    extractAudio: true, 
            //    outputAudioFormat: audioFormat, 
            //    extractVideo: true, 
            //    outputVideoFormat: videoFormat
            //).Wait();

            ExtractAudio(
                inputPath, 
                audioFormat
            );

            ExtractVideoWithoutAudio(
                inputPath, 
                videoFormat
            );
        }
    }
}
