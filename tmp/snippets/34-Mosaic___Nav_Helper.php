/**
 * Snippet ID: 34
 * Name: Mosaic — Nav Helper
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 1
 * Modified: 1
 * Size: 1018 bytes
 */

function mosaic_dynamic_nav($html) {
    $items = wp_get_nav_menu_items('main-menu');
    if (!$items) return $html;

    $current  = rtrim(home_url($_SERVER['REQUEST_URI']), '/');
    $book_url = home_url('/book-now/');
    $links    = \"
    \";

    foreach ($items as $item) {
        if (strtolower(trim($item->title)) === 'book now') {
            $book_url = $item->url;
            continue;
        }
        $active  = (rtrim($item->url, '/') === $current) ? ' class=\"active\"' : '';
        $links  .= '<a href=\"' . esc_url($item->url) . '\"' . $active . '>' . esc_html($item->title) . '</a>' . \"
    \";
    }

    $html = preg_replace(
        '/<div class=\"nav-links\">[\s\S]*?<\/div>/',
        '<div class=\"nav-links\">' . $links . '</div>',
        $html, 1
    );
    $html = preg_replace(
        '/<(?:button|a)[^>]+class=\"nav-book\"[^>]*>[\s\S]*?<\/(?:button|a)>/',
        '<a href=\"' . esc_url($book_url) . '\" class=\"nav-book\">Book Now</a>',
        $html, 1
    );
    return $html;
}