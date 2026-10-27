#!/bin/sh
# Full booking-flow test against a local mock of eZee and Razorpay. Nothing live is contacted.
#   scripts/flow-test/run.sh          builds a copy of api/ + book-now under $FLOW_TEST_DIR, runs ~155 checks, cleans up
# Needs php >= 8.1 (PHP_CLI_SERVER_WORKERS). Takes about 2 minutes (it waits out two real 15-18 s eZee timeouts).
set -eu
R="$(cd "$(dirname "$0")/../.." && pwd)"
export FLOW_TEST_DIR="${FLOW_TEST_DIR:-${TMPDIR:-/tmp}/mosaic-flow-test}"
H="$FLOW_TEST_DIR"
rm -rf "$H"; mkdir -p "$H/site" "$H/state"
cp -R "$R/api" "$H/site/api"; rm -f "$H/site/api/secrets.php" "$H/site/api/alert-email.php"
cp "$R/book-now.html" "$H/site/"; cp -R "$R/components" "$R/styles" "$H/site/"
cat > "$H/site/api/secrets.php" <<'PHP'
<?php
define('EZEE_HOTEL_CODE', 'MOCK1'); define('EZEE_API_KEY', 'mockkey'); define('EZEE_AUTH_CODE', 'mockauth');
define('EZEE_PAYMENT_ID', 'PAY1'); define('EZEE_CURRENCY_ID', 'INR1');
define('RAZORPAY_KEY_ID', 'rzp_test_mock'); define('RAZORPAY_KEY_SECRET', 'mocksecret'); define('RAZORPAY_WEBHOOK_SECRET', 'mockwebhooksecret');
define('ALERT_EMAIL', '');
define('EZEE_BASE_URL', 'http://127.0.0.1:8900/ezee/'); define('RAZORPAY_API_BASE', 'http://127.0.0.1:8900/razorpay');
PHP
for port in 8899 8900; do
  if lsof -ti tcp:$port >/dev/null 2>&1; then echo "port $port is in use (a previous run?). Free it: lsof -ti tcp:$port | xargs kill" >&2; exit 2; fi
done
export MOCK_STATE_DIR="$H/state" PHP_CLI_SERVER_WORKERS=4
php -S 127.0.0.1:8900 "$R/scripts/flow-test/mock.php" >"$H/mock.log" 2>&1 & MOCK=$!
# 30 s limit like typical shared hosting, so the slow-eZee case behaves as it would live.
php -d max_execution_time=30 -S 127.0.0.1:8899 -t "$H/site" >"$H/app.log" 2>&1 & APP=$!
# PHP_CLI_SERVER_WORKERS forks children that outlive the parent, so stop them by port.
trap 'for port in 8899 8900; do lsof -ti tcp:$port | xargs kill 2>/dev/null || true; done' EXIT INT TERM
sleep 2
php "$R/scripts/flow-test/flow-test.php"
