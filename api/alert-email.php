<?php
/**
 * Where booking alerts are emailed (see booking_alert() in lib/config.php).
 * Not a secret — just an address — so it lives here, in the repo and in the
 * normal deploy, instead of in secrets.php. A define() in secrets.php wins if
 * both exist.
 */
define('ALERT_EMAIL', 'mosaichostels@gmail.com');
