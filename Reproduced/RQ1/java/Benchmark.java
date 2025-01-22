import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class Benchmark {
    public static void main(String... args) throws IOException {
        if (args.length != 2) {
            System.out.println("Usage: java Benchmark <filename>");
            System.exit(1);
        }
        String content = "";
        StringBuilder builder = new StringBuilder();
        File file = new File(args[1]);
        InputStreamReader streamReader = new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8);
        BufferedReader bufferedReader = new BufferedReader(streamReader);

        while ((content = bufferedReader.readLine()) != null) 
            builder.append(content);
        bufferedReader.close();
        //System.out.println(builder.toString());
        measure(builder.toString(), args[0]);
    }

    // private static void measure(String data, String pattern) {
    //     long startTime = System.nanoTime();

    //     final Matcher matcher = Pattern.compile("^("+pattern+")$").matcher(data);
    //     boolean isMatch = matcher.matches();  // 使用matches()进行完全匹配
    //     long elapsed = System.nanoTime() - startTime;

    //     System.out.println(elapsed / 1e6 + " - " + (isMatch ? 1 : 0));  // 如果匹配返回1，否则返回0
    // }

    private static void measure(String data, String pattern) {
        long startTime = System.nanoTime();

        final Matcher matcher = Pattern.compile(pattern).matcher(data);
        int count = 0;
        while (matcher.find()) {
            ++count;
        }
        long elapsed = System.nanoTime() - startTime;

        System.out.println(elapsed / 1e6 + " - " + count);
    }
}
