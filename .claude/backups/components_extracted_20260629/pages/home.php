<?php
require_once __DIR__ . '/../loader.php';
$page_title = 'Home';
$meta_description = 'Mosaic Hostel Varanasi - Affordable stays near Assi Ghat.';
$content = file_get_contents(__DIR__ . '/home-content.html');
echo render_page($page_title, $content, $meta_description);
?>
