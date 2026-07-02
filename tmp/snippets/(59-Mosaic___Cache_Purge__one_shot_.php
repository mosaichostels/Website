/**
 * Snippet ID: (59
 * Name: Mosaic — Cache Purge (one-shot)
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 1
 * Modified: 0
 * Size: 506 bytes
 */

add_action('init', function() {
    if (class_exists('LiteSpeed_Cache_API')) {
        LiteSpeed_Cache_API::purge_all();
    } elseif (class_exists('\LiteSpeed\Core')) {
        do_action('litespeed_purge_all');
    } elseif (function_exists('litespeed_purge_all')) {
        litespeed_purge_all();
    }
    // Also try direct tag purge
    if (defined('LSCWP_V')) {
        do_action('litespeed_purge_all');
    }
    // Remove self after running
    $snippets = get_option('active_snippets', []);
}, 1);