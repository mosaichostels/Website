<?php
/**
 * Stay-date parsing and validation, shared by availability.php and
 * create-order.php. Kept out of config.php so it can be required on its own by
 * selftest.php, which has no secrets.php to satisfy that file's bootstrap.
 *
 * validate_stay_dates() calls json_error() from config.php; parse_strict_date()
 * is pure and is what the tests exercise.
 */

// Longest stay bookable online. Shared so the search and the order agree —
// they used to disagree, and create-order.php is directly reachable.
define('MAX_STAY_NIGHTS', 30);

/**
 * Strict Y-m-d parse. Two things the plain createFromFormat() call this
 * replaced got wrong:
 *  - no '!' prefix, so unspecified time components defaulted to the current
 *    clock time rather than midnight;
 *  - no getLastErrors() check, so PHP's lenient rollover accepted impossible
 *    dates — '2026-02-30' silently became 2 March, '2026-13-01' became 2027.
 *
 * getLastErrors() catches the rollovers but NOT sloppy widths: '2026-9-5' and
 * '26-09-05' both parse clean (the latter as year 0026). The shape check below
 * is what makes this actually strict. It matters because the raw string is
 * forwarded to eZee unmodified, and eZee specifies yyyy-mm-dd — and because the
 * browser's parseISO in book-now.js rejects the same input, so without this the
 * client and server disagree about what a valid date is.
 */
function parse_strict_date(string $value): ?DateTime {
  if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $value)) return null;
  $date = DateTime::createFromFormat('!Y-m-d', $value);
  $errors = DateTime::getLastErrors(); // false on PHP >= 8.2 when clean
  if ($date === false) return null;
  if (is_array($errors) && ($errors['warning_count'] > 0 || $errors['error_count'] > 0)) return null;
  return $date;
}

// Free-cancellation window, and the hour check-in opens. Both are stated in the
// policy shown to guests (book-now.html, "Hostel Rules & Policies"): free up to
// 72 hours before check-in, check-in from 1:00 PM.
define('FREE_CANCELLATION_HOURS', 72);
define('CHECKIN_HOUR', 13);

/**
 * Is a cancellation for this check-in date still inside the free window?
 * Decides whether a guest is told they'll be refunded, so it lives here as a
 * named, testable function rather than inline in cancel-booking.php.
 * Returns null when the date can't be read — callers must not promise either
 * way on null. Times are hotel-local; config.php pins the timezone to IST.
 */
function refund_due_for_checkin(?string $checkIn, ?int $now = null): ?bool {
  if ($checkIn === null || $checkIn === '') return null;
  if (!parse_strict_date($checkIn)) return null;
  $checkInAt = strtotime($checkIn . ' ' . str_pad((string)CHECKIN_HOUR, 2, '0', STR_PAD_LEFT) . ':00:00');
  if ($checkInAt === false) return null;
  return ($checkInAt - ($now ?? time())) >= FREE_CANCELLATION_HOURS * 3600;
}

/**
 * Validates a stay's dates and returns the night count. Both availability.php
 * and create-order.php go through this: create-order.php is reachable without
 * ever calling the search, and used to enforce strictly less than it, so a
 * crafted POST could create a real Razorpay order for a stay starting in 2020
 * or running 5,000 nights. Exits via json_error() on any problem.
 */
function validate_stay_dates(string $checkIn, string $checkOut): int {
  $dCheckIn = parse_strict_date($checkIn);
  $dCheckOut = parse_strict_date($checkOut);
  if (!$dCheckIn || !$dCheckOut) {
    json_error(400, 'Please provide valid check-in and check-out dates.');
  }
  if ($dCheckIn < new DateTime('today')) {
    json_error(400, 'Check-in date cannot be in the past.');
  }
  if ($dCheckOut <= $dCheckIn) {
    json_error(400, 'Check-out date must be after check-in date.');
  }
  $nights = (int)$dCheckIn->diff($dCheckOut)->days;
  if ($nights > MAX_STAY_NIGHTS) {
    json_error(400, 'Stays longer than ' . MAX_STAY_NIGHTS . ' nights can\'t be booked online — please WhatsApp us directly.');
  }
  return $nights;
}
