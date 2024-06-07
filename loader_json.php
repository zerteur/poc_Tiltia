<?php
header('Content-Type: application/json');

// Define the directory containing the JSON files
$directory = 'results/';

// Check if the directory exists
if (!is_dir($directory)) {
    echo json_encode(['error' => 'Directory not found']);
    exit;
}

// Read all files from the directory
$files = array_diff(scandir($directory), array('..', '.'));

// Prepare an array to hold filename and extracted date
$fileDatePairs = [];

// Extract dates from filenames and store them with filenames
foreach ($files as $file) {
    // Updated regex to match YYYYMMDD pattern
    if (preg_match('/(\d{4})(\d{2})(\d{2})/', $file, $matches)) {
        $date = "{$matches[1]}-{$matches[2]}-{$matches[3]}"; // Normalize date to YYYY-MM-DD
        $fileDatePairs[] = ['file' => $file, 'date' => $date];
    }
}

if (empty($fileDatePairs)) {
    echo json_encode(['error' => 'No valid date files found', 'debug' => $files]);
    exit;
}

// Sort files by date in descending order
usort($fileDatePairs, function ($a, $b) {
    return strtotime($b['date']) - strtotime($a['date']); // Descending order by actual date
});

// Prepare a structured response array grouped by date
$groupedData = [];

// Process each file in sorted order
foreach ($fileDatePairs as $pair) {
    $filePath = $directory . $pair['file'];
    $fileContents = file_get_contents($filePath);
    if (false === $fileContents) {
        echo json_encode(['error' => 'Unable to read file: ' . $pair['file']]);
        exit;
    }
    $jsonData = json_decode($fileContents, true);

    // Check for JSON errors
    if (json_last_error() != JSON_ERROR_NONE) {
        echo json_encode(['error' => 'Error decoding JSON from file: ' . $pair['file']]);
        exit;
    }

    // Group data by date
    foreach ($jsonData as $item) {
        $groupedData[$pair['date']][] = $item;
    }
}

// Output the data grouped by date
echo json_encode($groupedData);
?>
