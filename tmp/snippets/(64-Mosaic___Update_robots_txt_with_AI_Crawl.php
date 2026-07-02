/**
 * Snippet ID: (64
 * Name: Mosaic — Update robots.txt with AI Crawler Rules
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 10
 * Modified: 0
 * Size: 755 bytes
 */


// Update robots.txt to add AI crawler permissions (runs once on init)
add_action('init', function() {
    $option_key = 'mosaic_robots_ai_added';
    if (get_option($option_key)) return;

    $robots_path = get_home_path() . 'robots.txt';
    $ai_block = \"
# AI Crawlers — explicitly permitted
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

User-agent: Applebot-Extended
Allow: /
\";

    $current = file_exists($robots_path) ? file_get_contents($robots_path) : '';
    if (strpos($current, 'GPTBot') === false) {
        file_put_contents($robots_path, $current . $ai_block);
    }
    update_option($option_key, true);
});
