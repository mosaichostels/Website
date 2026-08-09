<?php
/**
 * Shared bootstrap for every api/*.php endpoint: loads secrets, sets JSON
 * headers, defines the pending-order storage path, and small response
 * helpers. Require this first thing in every endpoint.
 */

header('Content-Type: application/json');

$secretsFile = __DIR__ . '/../secrets.php';
if (!file_exists($secretsFile)) {
  http_response_code(500);
  echo json_encode(['error' => 'Server not configured: copy api/secrets.example.php to api/secrets.php and fill in credentials.']);
  exit;
}
require $secretsFile;

// eZee sandbox vs production is differentiated by which HotelCode/APIKey
// pair is in secrets.php, not by a different base URL.
define('EZEE_BASE_URL', 'https://live.ipms247.com/');

// Pending-order JSON files live OUTSIDE the web root (one level above the
// site's docroot) so they're never HTTP-reachable and untouched by
// deploy.sh's FTP sync. api/lib -> api -> docroot -> parent of docroot.
define('PENDING_ORDERS_DIR', dirname(__DIR__, 3) . '/ezee-pending-orders');

function ensure_pending_dirs() {
  foreach (['pending', 'processing', 'done', 'failed'] as $sub) {
    $dir = PENDING_ORDERS_DIR . '/' . $sub;
    if (!is_dir($dir)) mkdir($dir, 0700, true);
  }
}

function bookings_log(string $line) {
  ensure_pending_dirs();
  $ts = date('c');
  file_put_contents(PENDING_ORDERS_DIR . '/bookings.log', "[$ts] $line\n", FILE_APPEND | LOCK_EX);
}

function json_error(int $httpCode, string $message) {
  http_response_code($httpCode);
  echo json_encode(['error' => $message]);
  exit;
}

function json_ok(array $data) {
  echo json_encode($data);
  exit;
}

function read_json_body(): array {
  $raw = file_get_contents('php://input');
  $data = json_decode($raw, true);
  if (!is_array($data)) json_error(400, 'Invalid JSON body.');
  return $data;
}
