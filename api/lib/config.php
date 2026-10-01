<?php
/**
 * Shared bootstrap for every api/*.php endpoint: loads secrets, sets JSON
 * headers, defines the pending-order storage path, and small response
 * helpers. Require this first thing in every endpoint.
 */

header('Content-Type: application/json');

// Every date in this system is a hotel-local one: "today" for availability, the
// 72-hour cancellation boundary, check-in at 1:00 PM. Hosts default to UTC,
// which is 5h30m behind — enough to move a refund decision across the boundary
// and to make "today" yesterday for anyone searching before 05:30 IST.
date_default_timezone_set('Asia/Kolkata');

// Pure date helpers live in their own file so selftest.php can require them
// without this bootstrap's secrets check exiting first.
require_once __DIR__ . '/dates.php';

$secretsFile = __DIR__ . '/../secrets.php';
if (!file_exists($secretsFile)) {
  http_response_code(500);
  echo json_encode(['error' => 'Server not configured: copy api/secrets.example.php to api/secrets.php and fill in credentials.']);
  exit;
}
require $secretsFile;
// Alert address: secrets.php may define ALERT_EMAIL itself; otherwise fall back to
// the committed api/alert-email.php so no live-credentials file needs editing.
if (!defined('ALERT_EMAIL') && is_file(__DIR__ . '/../alert-email.php')) require __DIR__ . '/../alert-email.php';

// eZee sandbox vs production is differentiated by which HotelCode/APIKey
// pair is in secrets.php, not by a different base URL.
// secrets.php may pre-define EZEE_BASE_URL (tests point it at a local mock);
// production never does, so this stays the live endpoint.
if (!defined('EZEE_BASE_URL')) define('EZEE_BASE_URL', 'https://live.ipms247.com/');

// Pending-order JSON files live OUTSIDE the web root (one level above the
// site's docroot) so they're never HTTP-reachable and untouched by
// deploy.sh's FTP sync. api/lib -> api -> docroot -> parent of docroot.
define('PENDING_ORDERS_DIR', dirname(__DIR__, 3) . '/ezee-pending-orders');

function ensure_pending_dirs() {
  foreach (['pending', 'processing', 'done', 'failed', 'abandoned', 'ratelimit', 'refunds'] as $sub) {
    $dir = PENDING_ORDERS_DIR . '/' . $sub;
    if (!is_dir($dir)) mkdir($dir, 0700, true);
  }
}

function bookings_log(string $line) {
  ensure_pending_dirs();
  // Guest-supplied text reaches log lines (cancel email etc.). Newlines would
  // let a caller forge a whole line (a fake "CONFIRMED"), and eZee's APIKey
  // rides in the query string, so a cURL error naming the URL would leak it.
  $line = preg_replace('/[\x00-\x1f\x7f]+/', ' ', $line);
  $line = preg_replace('/(APIKey=)[^&\s"]+/i', '$1***', $line);
  $ts = date('c');
  file_put_contents(PENDING_ORDERS_DIR . '/bookings.log', "[$ts] $line\n", FILE_APPEND | LOCK_EX);
}

/**
 * Tell a human. Logging alone meant a stranded paid order was only ever found
 * by someone grepping bookings.log. Mails ALERT_EMAIL (define it in
 * secrets.php) and always logs, so a missing address degrades to the old
 * behaviour instead of failing.
 */
function booking_alert(string $subject, string $detail): void {
  bookings_log("ALERT $subject $detail");
  if (defined('ALERT_EMAIL') && ALERT_EMAIL !== '') {
    @mail(ALERT_EMAIL, '[Mosaic booking] ' . $subject, $detail);
  }
}

/** Reject anything but the expected verb; these endpoints never take others. */
function require_method(string $method): void {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== $method) {
    header('Allow: ' . $method);
    json_error(405, 'Method not allowed.');
  }
}

/**
 * Scalar string from decoded JSON/query input. A client can send an array or
 * number where a string is expected, which used to reach trim()/preg_replace()
 * and surface as a TypeError (HTTP 500, empty body) instead of a clean 400.
 */
function str_field(array $source, string $key): string {
  $v = $source[$key] ?? '';
  return is_string($v) ? trim($v) : '';
}

/**
 * Best guess at the requesting client's address.
 *
 * This account sits behind Sucuri (see the WAF note in lib/ezee.php), so
 * REMOTE_ADDR is the WAF's address and every guest would share one bucket.
 * X-Forwarded-For names the real client but is supplied by the caller and is
 * therefore spoofable at will.
 *
 * ponytail: a determined attacker rotates the header and walks straight past
 * the limiter below. That is accepted — this stops runaway clients, retry
 * loops and casual abuse, which is what has actually cost us anything. Real
 * enforcement belongs at the WAF/CDN, where the address can't be forged.
 */
function client_ip(): string {
  $forwarded = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? '';
  if ($forwarded !== '') {
    $first = trim(explode(',', $forwarded)[0]);
    if (filter_var($first, FILTER_VALIDATE_IP)) return $first;
  }
  return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
}

/**
 * Fixed-window per-client request cap. Exits with 429 once exceeded.
 *
 * Every create-order.php call costs a real eZee query, a real Razorpay order
 * and a file on disk, and cancel-booking.php is otherwise a free
 * reservation-number guessing oracle — neither had any ceiling.
 *
 * NEVER apply this to verify-payment.php: a single guest legitimately calls it
 * up to six times while the booking confirms (see VERIFY_RETRY_DELAYS in
 * book-now.js), and refusing one of those strands a paid booking.
 */
function rate_limit(string $bucket, int $maxHits, int $windowSeconds, ?string $subject = null): void {
  ensure_pending_dirs();
  // $subject replaces the client address as the counter key. Pass a fixed
  // string for a site-wide ceiling, or a reservation number to cap guesses
  // against one booking — both survive a caller rotating X-Forwarded-For.
  $file = PENDING_ORDERS_DIR . '/ratelimit/' . hash('sha256', $bucket . '|' . ($subject ?? client_ip())) . '.json';
  $handle = @fopen($file, 'c+');
  // Can't track: let the request through rather than locking out real guests
  // because of a disk problem. Failing open is the right call for a speed bump.
  if (!$handle) return;

  flock($handle, LOCK_EX);
  $now = time();
  $state = json_decode((string)stream_get_contents($handle), true);
  if (!is_array($state) || ($state['start'] ?? 0) + $windowSeconds <= $now) {
    $state = ['start' => $now, 'hits' => 0];
  }
  $state['hits']++;
  rewind($handle);
  ftruncate($handle, 0);
  fwrite($handle, json_encode($state));
  flock($handle, LOCK_UN);
  fclose($handle);

  if ($state['hits'] > $maxHits) {
    $retryAfter = max(1, ($state['start'] + $windowSeconds) - $now);
    header('Retry-After: ' . $retryAfter);
    bookings_log("RATELIMIT bucket=$bucket ip=" . client_ip() . " hits={$state['hits']}");
    json_error(429, 'Too many requests just now — please wait a moment and try again, or WhatsApp us.');
  }
}

function json_error(int $httpCode, string $message) {
  http_response_code($httpCode);
  echo json_encode(['error' => $message]);
  exit;
}

/**
 * An upstream (eZee/Razorpay) failure the guest can't act on. The real text is
 * logged; the guest gets a fixed, safe sentence.
 *
 * eZee's error strings are echoed straight from its API and have included
 * request context; returning them verbatim leaked internals to anyone who could
 * POST to these endpoints, and told the guest nothing useful either.
 */
function json_error_upstream(int $httpCode, string $publicMessage, string $detail) {
  bookings_log("UPSTREAM http=$httpCode detail=$detail");
  json_error($httpCode, $publicMessage);
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
