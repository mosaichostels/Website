<?php
require_once __DIR__ . '/../loader.php';
$page_title = 'Photo Gallery';
$meta_description = 'Explore Mosaic Hostel Varanasi through our photo gallery.';
$content = file_get_contents(__DIR__ . '/gallery-content.html');
echo render_page($page_title, $content, $meta_description);
?>
