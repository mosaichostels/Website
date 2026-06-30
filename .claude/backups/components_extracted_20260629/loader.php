<?php
/**
 * Page Loader - Orchestrates page structure from components
 * Loads: navbar, footer, CSS, page content, and JavaScript
 */

function get_navbar() {
    $file = __DIR__ . '/includes/navbar.html';
    if (file_exists($file)) {
        return file_get_contents($file);
    }
    return '';
}

function get_footer() {
    $file = __DIR__ . '/includes/footer.html';
    if (file_exists($file)) {
        return file_get_contents($file);
    }
    return '';
}

function get_css() {
    $file = __DIR__ . '/styles/global.css';
    if (file_exists($file)) {
        return '<style>' . file_get_contents($file) . '</style>';
    }
    return '';
}

function get_javascript() {
    $file = __DIR__ . '/js/main.js';
    if (file_exists($file)) {
        return '<script>' . file_get_contents($file) . '</script>';
    }
    return '';
}

function render_page($page_title, $page_content, $meta_description = '') {
    $navbar = get_navbar();
    $footer = get_footer();
    $css = get_css();
    $javascript = get_javascript();

    $html = <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$page_title} — Mosaic Hostel Varanasi</title>
    <meta name="description" content="{$meta_description}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap"></noscript>
    {$css}
</head>
<body>
    <h1 style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0">{$page_title} — Mosaic Hostel Varanasi</h1>
    <div id="cursor"></div>
    <div id="cursor-ring"></div>
    <div id="progress"></div>

    {$navbar}

    <main role="main">
        {$page_content}
    </main>

    {$footer}

    {$javascript}
</body>
</html>
HTML;

    return $html;
}
?>
