<?php
require_once __DIR__ . '/../loader.php';
$page_title = 'About Us';
$meta_description = 'Learn about Mosaic Hostel Varanasi.';
$content = file_get_contents(__DIR__ . '/about-content.html');
echo render_page($page_title, $content, $meta_description);
?>
