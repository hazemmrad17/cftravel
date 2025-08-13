<?php
/**
 * API Proxy for CFTravel IA Agent
 * Forwards requests from frontend to Python API server
 */

// Set CORS headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json');

// Handle preflight OPTIONS requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get the request path
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);

// Remove /api-proxy.php from the path
$api_path = str_replace('/api-proxy.php', '', $path);

// Python API server URL (running on same server)
$python_api_url = 'http://localhost:8000' . $api_path;

// Get request method
$method = $_SERVER['REQUEST_METHOD'];

// Get request body for POST/PUT requests
$request_body = '';
if (in_array($method, ['POST', 'PUT'])) {
    $request_body = file_get_contents('php://input');
}

// Prepare cURL request
$ch = curl_init();

// Set cURL options
curl_setopt_array($ch, [
    CURLOPT_URL => $python_api_url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => $method,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Accept: application/json'
    ]
]);

// Add request body for POST/PUT requests
if (!empty($request_body)) {
    curl_setopt($ch, CURLOPT_POSTFIELDS, $request_body);
}

// Execute the request
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);

curl_close($ch);

// Handle errors
if ($error) {
    http_response_code(500);
    echo json_encode([
        'error' => 'API Server Error',
        'message' => 'Unable to connect to Python API server',
        'details' => $error
    ]);
    exit();
}

// Set response code
http_response_code($http_code);

// Return the response
if ($response) {
    echo $response;
} else {
    echo json_encode([
        'error' => 'No Response',
        'message' => 'Python API server returned no response'
    ]);
}
?> 