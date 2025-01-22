using System;
using System.IO;
using System.Text.RegularExpressions;
using System.Diagnostics;

class Benchmark
{
    static void Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.WriteLine("Usage: benchmark <filename>");
            Environment.Exit(1);
        }

        StreamReader reader = new System.IO.StreamReader(args[1]);
        string data = reader.ReadToEnd();

        Benchmark.Measure(data, args[0]);
    }

    static void Measure(string data, string pattern)
    {
        Stopwatch stopwatch = Stopwatch.StartNew();

        MatchCollection matches = Regex.Matches(data, pattern);
        int count = matches.Count;

        stopwatch.Stop();

        Console.WriteLine(stopwatch.Elapsed.TotalMilliseconds.ToString("G", System.Globalization.CultureInfo.InvariantCulture) + " - " + count);
    }
    
    // static void Measure(string data, string pattern)
    // {
    //     Stopwatch stopwatch = Stopwatch.StartNew();

    //     string anchoredPattern = "^(" + pattern + ")$";
    //     bool isMatch = Regex.IsMatch(data, anchoredPattern);
    //     int count = isMatch ? 1 : 0;

    //     stopwatch.Stop();

    //     Console.WriteLine(stopwatch.Elapsed.TotalMilliseconds.ToString("G", System.Globalization.CultureInfo.InvariantCulture) + " - " + count);
    // }
}
