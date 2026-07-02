/**
 * Snippet ID: (63
 * Name: Mosaic — www Redirect + AI Crawler Permissions
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 10
 * Modified: 0
 * Size: 993 bytes
 */


// ── WWW Redirect + AI Crawler permissions ─────────────────────────────────────

// 1. Force www — 301 redirect non-www to www
add_action('template_redirect', function() {
    if (headers_sent()) return;
    $host = $_SERVER['HTTP_HOST'] ?? '';
    if ($host && strpos($host, 'www.') !== 0) {
        $redirect = 'https://www.' . $host . ($_SERVER['REQUEST_URI'] ?? '/');
        header('Location: ' . $redirect, true, 301);
        exit;
    }
}, -10);

// 2. robots.txt — AI crawlers explicitly permitted
add_filter('robots_txt', function($output, $public) {
    $output .= \"
# AI Crawlers — explicitly permitted
\";
    $output .= \"User-agent: GPTBot
Allow: /

\";
    $output .= \"User-agent: ClaudeBot
Allow: /

\";
    $output .= \"User-agent: PerplexityBot
Allow: /

\";
    $output .= \"User-agent: Googlebot-Extended
Allow: /

\";
    $output .= \"User-agent: OAI-SearchBot
Allow: /

\";
    $output .= \"User-agent: Applebot-Extended
Allow: /
\";
    return $output;
}, 10, 2);
