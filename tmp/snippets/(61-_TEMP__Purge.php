/**
 * Snippet ID: (61
 * Name: [TEMP] Purge
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 1
 * Modified: 0
 * Size: 67 bytes
 */

add_action('init',function(){do_action('litespeed_purge_all');},1);