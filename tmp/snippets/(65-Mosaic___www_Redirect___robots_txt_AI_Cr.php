/**
 * Snippet ID: (65
 * Name: Mosaic — www Redirect + robots.txt AI Crawlers (dynamic)
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 10
 * Modified: 1
 * Size: 1165 bytes
 */


// ── WWW Redirect + robots.txt with AI Crawlers ────────────────────────────────

// 1. Force www — 301 redirect non-www to www
add_action('template_redirect', function() {
    if (headers_sent()) return;
    $host = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : '';
    if ($host && strpos($host, 'www.') !== 0) {
        $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '/';
        header('Location: https://www.' . $host . $uri, true, 301);
        exit;
    }
}, -10);

// 2. Ensure robots.txt has AI crawler rules (write on every init until confirmed)
add_action('init', function() {
    $robots_path = get_home_path() . 'robots.txt';
    $content = \"User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: https://www.mosaichostels.com/wp-sitemap.xml

# AI Crawlers
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Googlebot-Extended
Allow: /

User-agent: OAI-SearchBot
Allow: /
\";

    $current = @file_get_contents($robots_path);
    if (strpos($current, 'GPTBot') === false) {
        @file_put_contents($robots_path, $content);
    }
}, 999);
