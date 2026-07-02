/**
 * Snippet ID: (60
 * Name: [TEMP] Cache Purge
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 1
 * Modified: 0
 * Size: 816 bytes
 */

add_action(\"init\", function() {
    // Delete LiteSpeed cache files directly
    $cache_dirs = array(
        WP_CONTENT_DIR . \"/cache/litespeed/\",
        WP_CONTENT_DIR . \"/litespeed/\",
    );
    foreach ($cache_dirs as $dir) {
        if (is_dir($dir)) {
            $files = new RecursiveIteratorIterator(
                new RecursiveDirectoryIterator($dir, RecursiveDirectoryIterator::SKIP_DOTS),
                RecursiveIteratorIterator::CHILD_FIRST
            );
            foreach ($files as $file) {
                if ($file->isFile() && in_array($file->getExtension(), array(\"html\",\"css\",\"js\"))) {
                    @unlink($file->getPathname());
                }
            }
        }
    }
    do_action(\"litespeed_purge_all\");
    do_action(\"litespeed_api_purge_all\");
}, 1);
