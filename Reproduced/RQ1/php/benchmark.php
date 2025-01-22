<?php

if (count($argv) !== 3) {
    echo 'Usage: php benchmark.php <filename>';
    die(1);
}

$data  = file_get_contents($argv[2]);
//echo $data . PHP_EOL;
measure($data, '/' . $argv[1] . '/');


function measure($data, $pattern) {
    $startTime = microtime(true);

    $count = preg_match_all($pattern, $data, $matches);

    $elapsed = (microtime(true) - $startTime) * 1e3;

    echo $elapsed . ' - ' . $count . PHP_EOL;
}


// function measure($data, $pattern) {
//     $startTime = microtime(true);

//     $pattern = '^(' . trim($pattern, '/') . ')$';
//     $pattern = '/' . $pattern . '/';
//     $count = preg_match($pattern, $data, $matches);

//     $elapsed = (microtime(true) - $startTime) * 1e3;

//     echo $elapsed . ' - ' . $count . PHP_EOL;
// }
