<?php
// Simple API Proxy for CFTravel AI Agent
// This forwards API calls to the Python server

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get the API endpoint from the URL
$request_uri = $_SERVER['REQUEST_URI'];
$api_path = str_replace('/api-proxy.php', '', $request_uri);

// Python server URL (adjust if needed)
$python_server = 'http://localhost:8000';

// Forward the request to Python server
$url = $python_server . $api_path;

// Get request data
$input = file_get_contents('php://input');
$method = $_SERVER['REQUEST_METHOD'];

// Set up cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($input)
]);

// Execute request
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Return response
http_response_code($http_code);
echo $response;
?> 