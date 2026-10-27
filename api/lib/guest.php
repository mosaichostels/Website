<?php
/**
 * The values the booking form offers for the optional guest fields, and the check that keeps anything else out of a
 * paid booking.
 *
 * Live eZee ACCEPTS other text here (verified 2026-10-27: "Mâle", "M.", a translated country and a blank last name were
 * all booked), so this is data hygiene, not what failed the 27 Sep order (that was a multi-night stay, see
 * ezee_daywise_rates()). A browser that translated the page used to submit its own translation ("Mâle", "12h00 - 15h00"),
 * which then sat in the guest record and the special request. create-order.php refuses such a request up front,
 * before any Razorpay order exists. These lists mirror book-now.html (title, gender, arrival) and COUNTRIES in
 * components/book-now.js; selftest.php fails if they drift apart.
 */
const GUEST_TITLES = ['Mr.', 'Ms.', 'Mrs.'];
// "Other" is offered by the form; live eZee accepts it (verified 2026-10-27).
const GUEST_GENDERS = ['Male', 'Female', 'Other'];
const GUEST_ARRIVAL_TIMES = ['Before 12:00 PM', '12:00 PM – 3:00 PM', '3:00 PM – 6:00 PM', '6:00 PM – 9:00 PM', 'After 9:00 PM'];
const GUEST_COUNTRIES = [
  'India', 'Afghanistan', 'Australia', 'Austria', 'Bangladesh', 'Belgium', 'Bhutan', 'Brazil', 'Canada',
  'China', 'Denmark', 'Egypt', 'Finland', 'France', 'Germany', 'Greece', 'Hong Kong', 'Indonesia', 'Iran',
  'Iraq', 'Ireland', 'Israel', 'Italy', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait', 'Malaysia',
  'Maldives', 'Mexico', 'Myanmar', 'Nepal', 'Netherlands', 'New Zealand', 'Nigeria', 'Norway', 'Oman',
  'Pakistan', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Russia', 'Saudi Arabia', 'Singapore',
  'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sweden', 'Switzerland', 'Thailand', 'Turkey', 'UAE',
  'Ukraine', 'United Kingdom', 'United States', 'Vietnam'
];

/**
 * Null when every supplied value is on its list; otherwise a message for the guest. An empty value is
 * fine (all four fields are optional on the form). Exact, case-sensitive match: it is eZee's own spelling.
 */
function guest_values_error(array $guest, string $nationality, string $arrivalTime): ?string {
  $checks = [
    ['title', $guest['title'] ?? '', GUEST_TITLES],
    ['gender', $guest['gender'] ?? '', GUEST_GENDERS],
    ['nationality', $nationality, GUEST_COUNTRIES],
    ['arrival time', $arrivalTime, GUEST_ARRIVAL_TIMES],
  ];
  foreach ($checks as [$label, $value, $allowed]) {
    if ($value !== '' && !in_array($value, $allowed, true)) {
      return "Please choose a valid $label from the list (if your browser translated this page, reload it and try again).";
    }
  }
  return null;
}

/**
 * Free-text guest fields: refuse a blank first name and oversized text before payment.
 * Lengths count characters, not bytes (Hindi and accented names). Null when fine, else a message for the guest.
 */
function guest_text_error(string $firstName, string $lastName, string $specialRequest, string $email): ?string {
  // Live eZee accepted a blank first AND last name (2026-10-27), so only a blank first name is refused here, as
  // the minimum for a usable booking. The form still asks for both. Both are length/control-character checked.
  $firstName = trim($firstName); $lastName = trim($lastName);
  if ($firstName === '') return 'Please enter your first name as it appears on your ID.';
  foreach ([['first name', $firstName], ['last name', $lastName]] as [$label, $name]) {
    if (guest_chars($name) > 60 || preg_match('/[\x00-\x1f\x7f]/', $name)) return "Please check your $label: up to 60 letters, no line breaks.";
  }
  if (guest_chars($specialRequest) > 500) return 'Please keep your special request under 500 characters.';
  if (strlen($email) > 254) return 'Please provide a valid email address.';
  return null;
}

/** Characters, not bytes (Hindi/accented names). mbstring is not assumed on the host; an invalid UTF-8 string counts as too long. */
function guest_chars(string $s): int {
  if (function_exists('mb_strlen')) return mb_strlen($s);
  $n = preg_match_all('/./su', $s);
  return $n === false ? PHP_INT_MAX : $n;
}
