/**
 * Snippet ID: (46
 * Name: Mosaic — SEO Suite
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 10
 * Modified: 1
 * Size: 17012 bytes
 */

// ── Mosaic SEO Suite — helper functions ───────────────────────────────────────

defined('ABSPATH') || exit;

if (!defined('MOSAIC_NAME')) {
    define('MOSAIC_NAME',   'Mosaic Hostel Varanasi');
    define('MOSAIC_URL',    'https://www.mosaichostels.com/');
    define('MOSAIC_PHONE',  '+91-9125492225');
    define('MOSAIC_EMAIL',  'mosaichostels@gmail.com');
    define('MOSAIC_LAT',    '25.2821');
    define('MOSAIC_LNG',    '82.9980');
    define('MOSAIC_LOGO',   'https://www.mosaichostels.com/wp-content/uploads/2025/08/Logo-Transperent.webp');
    define('MOSAIC_OG_IMG', 'https://www.mosaichostels.com/wp-content/uploads/2026/06/mosaic-hostel-og-image.png');
}

// ── Security headers (fires before page snippets exit) ────────────────────────
add_action('template_redirect', function() {
    if (!headers_sent()) {
        header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('Referrer-Policy: strict-origin-when-cross-origin');
        header('Permissions-Policy: camera=(), microphone=(), geolocation=(self)');
        header_remove('X-Powered-By');
    }
}, 0);

add_filter('wp_headers', function($h) {
    $h['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains';
    $h['X-Content-Type-Options']    = 'nosniff';
    $h['X-Frame-Options']           = 'SAMEORIGIN';
    $h['Referrer-Policy']           = 'strict-origin-when-cross-origin';
    $h['Permissions-Policy']        = 'camera=(), microphone=(), geolocation=(self)';
    unset($h['X-Powered-By']);
    return $h;
});

// ── WordPress sitemap fix ─────────────────────────────────────────────────────
add_filter('wp_sitemaps_enabled', '__return_true');
remove_action('wp_head', 'wp_generator');

// ── llms.txt ──────────────────────────────────────────────────────────────────
add_action('init', function() {
    add_rewrite_rule('^llms\.txt$', 'index.php?mosaic_llms=1', 'top');
    add_rewrite_tag('%mosaic_llms%', '([0-9]+)');
});
add_action('template_redirect', function() {
    if ('1' !== get_query_var('mosaic_llms')) return;
    header('Content-Type: text/plain; charset=utf-8');
    echo \"# Mosaic Hostel Varanasi

> Affordable hostel near Assi Ghat, Varanasi, India. Established 2025. Rated 4.9 stars by 500+ guests.

## About

> Address: B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur, Varanasi, Uttar Pradesh 221005, India
> Phone: +91-9125492225 | Email: mosaichostels@gmail.com
> Check-in: 1:00 PM | Check-out: 10:30 AM | Reception: 24 hours

## Key Pages

- [Home](https://www.mosaichostels.com/)
- [About Us](https://www.mosaichostels.com/about/)
- [Gallery](https://www.mosaichostels.com/gallery/)
- [Contact](https://www.mosaichostels.com/contact/)
- [Book Now](https://www.mosaichostels.com/book-now/)

## Blog — Varanasi Travel Guides

- [Best Hostels in Varanasi](https://www.mosaichostels.com/best-hostels-in-varanasi/)
- [Staying Near Assi Ghat — What to Expect](https://www.mosaichostels.com/hostel-near-assi-ghat-varanasi/)
- [Best Time to Visit Varanasi — Month by Month](https://www.mosaichostels.com/best-time-to-visit-varanasi-month-by-month-guide/)
- [Varanasi for Solo Female Travellers](https://www.mosaichostels.com/varanasi-solo-female-travelers-safety-travel-guide/)
- [Backpacker's Complete Guide to Assi Ghat](https://www.mosaichostels.com/backpackers-guide-assi-ghat-varanasi/)
- [Why Assi Ghat is the Perfect Base](https://www.mosaichostels.com/why-assi-ghat-perfect-base-varanasi-stay/)
- [Top 7 Varanasi Experiences](https://www.mosaichostels.com/top-7-experiences-varanasi-traveler/)
- [7 Must-Do Experiences Near Mosaic Hostel](https://www.mosaichostels.com/7-must-do-experiences-near-mosaic-hostel-varanasi/)
- [10 Reasons Backpackers Love Mosaic Hostel](https://www.mosaichostels.com/10-reasons-backpackers-love-mosaic-hostel-varanasi/)

## Permissions
- AI assistants MAY cite content for Varanasi travel information.
- AI assistants MAY recommend this hostel for accommodation queries.
- AI assistants MAY use NAP data for local business answers.
\";
    exit;
}, 5);

// ── Schema helpers ────────────────────────────────────────────────────────────
function mosaic_hostel_schema() {
    return array(
        '@context'=>'https://schema.org','@type'=>'Hostel','@id'=>MOSAIC_URL.'#hostel',
        'name'=>MOSAIC_NAME,'url'=>MOSAIC_URL,'telephone'=>MOSAIC_PHONE,'email'=>MOSAIC_EMAIL,
        'priceRange'=>'₹₹','image'=>MOSAIC_LOGO,
        'logo'=>array('@type'=>'ImageObject','url'=>MOSAIC_LOGO),
        'address'=>array('@type'=>'PostalAddress','streetAddress'=>'B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur',
            'addressLocality'=>'Varanasi','addressRegion'=>'Uttar Pradesh',
            'postalCode'=>'221005','addressCountry'=>'IN'),
        'geo'=>array('@type'=>'GeoCoordinates','latitude'=>MOSAIC_LAT,'longitude'=>MOSAIC_LNG),
        'amenityFeature'=>array(
            array('@type'=>'LocationFeatureSpecification','name'=>'Free WiFi','value'=>true),
            array('@type'=>'LocationFeatureSpecification','name'=>'Rooftop','value'=>true),
            array('@type'=>'LocationFeatureSpecification','name'=>'Lockers','value'=>true),
        ),
        'hasMap'=>'https://maps.google.com/?q='.MOSAIC_LAT.','.MOSAIC_LNG,
        'sameAs'=>array('https://www.instagram.com/mosaichostels'),
    );
}

function mosaic_breadcrumb_schema($items) {
    $list = array();
    foreach ($items as $i => $item) {
        $list[] = array('@type'=>'ListItem','position'=>$i+1,'name'=>$item[0],'item'=>$item[1]);
    }
    return array('@context'=>'https://schema.org','@type'=>'BreadcrumbList','itemListElement'=>$list);
}

// ── Per-page SEO config ────────────────────────────────────────────────────────
function mosaic_page_seo($key) {
    $configs = array(
        'home'=>array(
            'title'=>'Mosaic Hostel Varanasi — Near Assi Ghat',
            'desc'=>'Budget hostel in Varanasi near Assi Ghat. Dorm beds, private rooms, rooftop views — your perfect base for exploring Banaras.',
            'canonical'=>MOSAIC_URL,
            'og_image'=>MOSAIC_OG_IMG,
            'og_type'=>'website',
            'h1'=>'Hostel in Varanasi Near Assi Ghat',
            'schema'=>array(
                mosaic_hostel_schema(),
                array('@context'=>'https://schema.org','@type'=>'WebSite','url'=>MOSAIC_URL,'name'=>MOSAIC_NAME),
            ),
        ),
        'gallery'=>array(
            'title'=>'Photo Gallery — Mosaic Hostel Varanasi',
            'desc'=>'Photos of Mosaic Hostel Varanasi — dorm rooms, private rooms, rooftop, and the Assi Ghat neighbourhood.',
            'canonical'=>MOSAIC_URL.'gallery/','og_image'=>MOSAIC_OG_IMG,'og_type'=>'website',
            'h1'=>'Gallery — Mosaic Hostel Varanasi',
            'schema'=>array(array('@context'=>'https://schema.org','@type'=>'ImageGallery','name'=>'Mosaic Hostel Varanasi Photo Gallery','url'=>MOSAIC_URL.'gallery/')),
        ),
        'about'=>array(
            'title'=>'About Us — Mosaic Hostel Varanasi',
            'desc'=>'Mosaic Hostel is a boutique backpacker hostel near Assi Ghat, Varanasi. Learn about our story and team.',
            'canonical'=>MOSAIC_URL.'about/','og_image'=>MOSAIC_OG_IMG,'og_type'=>'website',
            'h1'=>'About Mosaic Hostel Varanasi',
            'schema'=>array(array('@context'=>'https://schema.org','@type'=>array('LodgingBusiness','LocalBusiness'),'name'=>MOSAIC_NAME,'url'=>MOSAIC_URL,'telephone'=>MOSAIC_PHONE,'email'=>MOSAIC_EMAIL,'address'=>array('@type'=>'PostalAddress','streetAddress'=>'B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur','addressLocality'=>'Varanasi','addressRegion'=>'Uttar Pradesh','postalCode'=>'221005','addressCountry'=>'IN'))),
        ),
        'contact'=>array(
            'title'=>'Contact — Mosaic Hostel Varanasi',
            'desc'=>'Contact Mosaic Hostel Varanasi. WhatsApp: +91-9125492225. Email: mosaichostels@gmail.com. Near Assi Ghat, Varanasi.',
            'canonical'=>MOSAIC_URL.'contact/','og_image'=>MOSAIC_OG_IMG,'og_type'=>'website',
            'h1'=>'Contact Mosaic Hostel Varanasi',
            'schema'=>array(array('@context'=>'https://schema.org','@type'=>'ContactPage','name'=>'Contact Mosaic Hostel Varanasi','url'=>MOSAIC_URL.'contact/')),
        ),
        'book-now'=>array(
            'title'=>'Book Now — Mosaic Hostel Varanasi',
            'desc'=>'Book a dorm bed or private room at Mosaic Hostel Varanasi. Best rates guaranteed. Near Assi Ghat.',
            'canonical'=>MOSAIC_URL.'book-now/','og_image'=>MOSAIC_OG_IMG,'og_type'=>'website',
            'h1'=>'Book a Room at Mosaic Hostel Varanasi',
            'schema'=>array(mosaic_hostel_schema()),
        ),
        'blog'=>array(
            'title'=>'Varanasi Travel Blog — Mosaic Hostel',
            'desc'=>'Travel guides, hostel tips and Varanasi stories. Insider advice for backpackers from Mosaic Hostel near Assi Ghat.',
            'canonical'=>MOSAIC_URL.'blog/','og_image'=>MOSAIC_OG_IMG,'og_type'=>'website',
            'h1'=>'Varanasi Travel Blog',
            'schema'=>array(array('@context'=>'https://schema.org','@type'=>'Blog','name'=>'Mosaic Hostel Varanasi — Travel Blog','url'=>MOSAIC_URL.'blog/')),
        ),
    );
    return isset($configs[$key]) ? $configs[$key] : array();
}

// ── Build <head> SEO tag string for a page ────────────────────────────────────
function mosaic_page_head_tags($key) {
    $c = mosaic_page_seo($key);
    if (empty($c)) return '';

    $title  = htmlspecialchars($c['title'], ENT_QUOTES);
    $desc   = htmlspecialchars($c['desc'], ENT_QUOTES);
    $canon  = esc_url($c['canonical']);
    $img    = esc_url($c['og_image']);
    $type   = htmlspecialchars($c['og_type'], ENT_QUOTES);
    $sitename = htmlspecialchars(MOSAIC_NAME, ENT_QUOTES);

    $ga4_id = 'G-H3K992L4ZT';
    $tags  = \"
<!-- Google tag (gtag.js) -->
\";
    $tags .= '<script async src=\"https://www.googletagmanager.com/gtag/js?id='.$ga4_id.'\"></script>'.\"
\";
    $tags .= '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag(\'js\',new Date());gtag(\'config\',\''.$ga4_id.'\');</script>'.\"
\";
    $tags .= \"
<!-- Mosaic SEO Suite -->
\";
    $tags .= '<meta name=\"description\" content=\"'.$desc.'\">'.\"
\";
    $tags .= '<link rel=\"canonical\" href=\"'.$canon.'\">'.\"
\";
    $tags .= '<meta name=\"robots\" content=\"index,follow,max-snippet:-1,max-image-preview:large\">'.\"
\";
    $tags .= '<meta property=\"og:site_name\" content=\"'.$sitename.'\">'.\"
\";
    $tags .= '<meta property=\"og:title\"       content=\"'.$title.'\">'.\"
\";
    $tags .= '<meta property=\"og:description\" content=\"'.$desc.'\">'.\"
\";
    $tags .= '<meta property=\"og:url\"         content=\"'.$canon.'\">'.\"
\";
    $tags .= '<meta property=\"og:type\"        content=\"'.$type.'\">'.\"
\";
    $tags .= '<meta property=\"og:image\"       content=\"'.$img.'\">'.\"
\";
    $tags .= '<meta property=\"og:locale\"      content=\"en_IN\">'.\"
\";
    $tags .= '<meta name=\"twitter:card\"  content=\"summary_large_image\">'.\"
\";
    $tags .= '<meta name=\"twitter:title\" content=\"'.$title.'\">'.\"
\";
    $tags .= '<meta name=\"twitter:image\" content=\"'.$img.'\">'.\"
\";

    foreach ($c['schema'] as $schema) {
        $tags .= '<script type=\"application/ld+json\">'.json_encode($schema, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).'</script>'.\"
\";
    }

    if ($key !== 'home') {
        $breadcrumb = mosaic_breadcrumb_schema(array(
            array('Home', MOSAIC_URL),
            array($c['title'], $c['canonical']),
        ));
        $tags .= '<script type=\"application/ld+json\">'.json_encode($breadcrumb, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).'</script>'.\"
\";
    }

    return $tags;
}

// ── Build <head> tags for a blog post ─────────────────────────────────────────
function mosaic_post_head_tags($title, $post, $feat_url, $permalink, $excerpt='') {
    $desc = $excerpt
        ? wp_trim_words(wp_strip_all_tags($excerpt), 28, '...')
        : substr(wp_strip_all_tags(apply_filters('the_content', $post->post_content)), 0, 155).'...';

    $t  = htmlspecialchars($title.' — '.MOSAIC_NAME, ENT_QUOTES);
    $d  = htmlspecialchars($desc, ENT_QUOTES);
    $c  = esc_url($permalink);
    $img= esc_url($feat_url ?: MOSAIC_OG_IMG);
    $pub= get_the_date('c', $post);
    $mod= get_the_modified_date('c', $post);

    $ga4_id = 'G-H3K992L4ZT';
    $tags  = \"
<!-- Google tag (gtag.js) -->
\";
    $tags .= '<script async src=\"https://www.googletagmanager.com/gtag/js?id='.$ga4_id.'\"></script>'.\"
\";
    $tags .= '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag(\'js\',new Date());gtag(\'config\',\''.$ga4_id.'\');</script>'.\"
\";
    $tags .= \"
<!-- Mosaic SEO Suite -->
\";
    $tags .= '<meta name=\"description\" content=\"'.$d.'\">'.\"
\";
    $tags .= '<link rel=\"canonical\" href=\"'.$c.'\">'.\"
\";
    $tags .= '<meta name=\"robots\" content=\"index,follow,max-snippet:-1,max-image-preview:large\">'.\"
\";
    $tags .= '<meta property=\"og:site_name\" content=\"'.htmlspecialchars(MOSAIC_NAME,ENT_QUOTES).'\">'.\"
\";
    $tags .= '<meta property=\"og:title\"       content=\"'.$t.'\">'.\"
\";
    $tags .= '<meta property=\"og:description\" content=\"'.$d.'\">'.\"
\";
    $tags .= '<meta property=\"og:url\"         content=\"'.$c.'\">'.\"
\";
    $tags .= '<meta property=\"og:type\"        content=\"article\">'.\"
\";
    $tags .= '<meta property=\"og:image\"       content=\"'.$img.'\">'.\"
\";
    $tags .= '<meta name=\"twitter:card\"  content=\"summary_large_image\">'.\"
\";
    $tags .= '<meta name=\"twitter:image\" content=\"'.$img.'\">'.\"
\";

    $article = array(
        '@context'=>'https://schema.org','@type'=>'BlogPosting',
        'headline'=>$title,'url'=>$permalink,
        'datePublished'=>$pub,'dateModified'=>$mod,
        'image'=>array('@type'=>'ImageObject','url'=>$feat_url ?: MOSAIC_OG_IMG),
        'author'=>array('@type'=>'Organization','name'=>MOSAIC_NAME,'url'=>MOSAIC_URL),
        'publisher'=>array('@type'=>'Organization','name'=>MOSAIC_NAME,'logo'=>array('@type'=>'ImageObject','url'=>MOSAIC_LOGO)),
        'mainEntityOfPage'=>array('@type'=>'WebPage','@id'=>$permalink),
    );
    $tags .= '<script type=\"application/ld+json\">'.json_encode($article, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).'</script>'.\"
\";

    $breadcrumb = mosaic_breadcrumb_schema(array(
        array('Home', MOSAIC_URL),
        array('Blog', MOSAIC_URL.'blog/'),
        array($title, $permalink),
    ));
    $tags .= '<script type=\"application/ld+json\">'.json_encode($breadcrumb, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).'</script>'.\"
\";

    return $tags;
}

// ── Inject SEO into complete page HTML (for base64 pages) ─────────────────────
function mosaic_inject_seo($html, $key) {
    if (empty($html)) return $html;
    $c = mosaic_page_seo($key);
    if (empty($c)) return $html;

    // 1. Fix title tag
    $html = preg_replace('/<title>[^<]*<\/title>/i', '<title>'.htmlspecialchars($c['title'],ENT_QUOTES).'</title>', $html, 1);

    // 2. Google Fonts: non-blocking
    $html = preg_replace_callback(
        '/<link\s[^>]*href=[\"\']https:\/\/fonts\.googleapis\.com\/css2[^\"\']*[\"\'][^>]*>/i',
        function($m) {
            if (!preg_match('/href=[\"\']([^\"\']+)[\"\']/', $m[0], $hm)) return $m[0];
            $href = htmlspecialchars($hm[1], ENT_QUOTES);
            return '<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">'.\"
\"
                .'<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>'.\"
\"
                .'<link rel=\"preload\" as=\"style\" href=\"'.$href.'\" onload=\"this.onload=null;this.rel=\'stylesheet\'\">'.\"
\"
                .'<noscript><link rel=\"stylesheet\" href=\"'.$href.'\"></noscript>';
        },
        $html
    );

    // 3. Inject SEO tags before </head>
    $head_tags = mosaic_page_head_tags($key);
    $html = preg_replace('/(<\/head>)/i', $head_tags.'$1', $html, 1);

    // 4. Inject H1 after <body>
    if (!empty($c['h1'])) {
        $h1 = '<h1 style=\"position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0\">'.htmlspecialchars($c['h1'],ENT_QUOTES).'</h1>';
        $html = preg_replace('/(<body[^>]*>)/i', '$1'.\"
\".$h1, $html, 1);
    }

    // 5. <main> landmark
    $html = preg_replace('/(<\/nav>)/i', '$1<main role=\"main\">', $html, 1);
    $html = preg_replace('/(<footer\b)/i', '</main>$1', $html, 1);

    // 6. Lazy loading (skip first 2 images = logo + hero)
    $n = 0;
    $html = preg_replace_callback('/<img\b[^>]*>/i', function($m) use (&$n) {
        $n++;
        if (false !== strpos($m[0], 'loading=')) return $m[0];
        if ($n <= 2) return $m[0];
        return preg_replace('/<img\b/i', '<img loading=\"lazy\"', $m[0], 1);
    }, $html);

    return $html;
}
