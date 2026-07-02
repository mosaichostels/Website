/**
 * Snippet ID: (62
 * Name: 
 * Scope: global
 * Priority: 10
 * Active: 0
 * Created: 10
 * Modified: 0
 * Size: 14754 bytes
 */


// ============================================================
// MOSAIC HOSTEL VARANASI — SEO MASTER SNIPPET
// Meta descriptions · Schema · Canonical · www redirect · AI
// ============================================================

// 1. WWW REDIRECT — canonicalize to www
add_action('template_redirect', function() {
    if (!is_admin() && isset($_SERVER['HTTP_HOST']) && strpos($_SERVER['HTTP_HOST'], 'www.') !== 0) {
        $redirect = 'https://www.' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
        wp_redirect($redirect, 301);
        exit;
    }
});

// 2. META DESCRIPTIONS
add_action('wp_head', function() {
    $descriptions = [
        'home'     => 'Stay at Mosaic Hostel Varanasi — near Assi Ghat with private rooms & dorms. Rated 4.9★ by 500+ guests. Book your Varanasi experience.',
        'about'    => 'Learn about Mosaic Hostel Varanasi — a community-first hostel near Assi Ghat. Our story, team, and what makes us different.',
        'contact'  => 'Contact Mosaic Hostel Varanasi — B1/85C, Assi Ghat Rd, Varanasi UP 221005. Call +91 91254 92225 or WhatsApp. Open 24 hours.',
        'gallery'  => 'Photo gallery of Mosaic Hostel Varanasi — rooms, rooftop, common areas, and hostel life near Assi Ghat. See before you book.',
        'book-now' => 'Book your stay at Mosaic Hostel Varanasi — affordable rooms & dorms near Assi Ghat. Rated 4.9★ by 500+ guests. Best rates direct.',
        'blog'     => 'Varanasi travel blog by Mosaic Hostel — guides on Assi Ghat, safety, best experiences, and insider travel advice.',
        'best-hostels-in-varanasi'                           => 'Looking for the best hostels in Varanasi? Honest 2025 guide covering location, vibe, amenities, and what to expect near the Ghats.',
        'hostel-near-assi-ghat-varanasi'                     => 'Staying near Assi Ghat, Varanasi? Here\'s exactly what to expect — the neighbourhood, morning rituals, local food, and where to stay.',
        '10-reasons-backpackers-love-mosaic-hostel-varanasi' => '10 reasons backpackers choose Mosaic Hostel Varanasi — rooftop views, community vibes, and a prime Assi Ghat location.',
        'backpackers-guide-assi-ghat-varanasi'               => 'Complete backpacker\'s guide to Assi Ghat, Varanasi — morning ceremonies, boat rides, chai spots, walking routes, and where to stay.',
        'top-7-experiences-varanasi-traveler'                => 'Top 7 experiences every Varanasi traveller must have — Ganga Aarti, Subah-e-Banaras, ancient lanes, and more.',
        'why-assi-ghat-perfect-base-varanasi-stay'           => 'Why Assi Ghat is the best base for your Varanasi stay — authentic atmosphere, close to all ghats, safe neighbourhood.',
        '7-must-do-experiences-near-mosaic-hostel-varanasi'  => '7 must-do experiences near Mosaic Hostel Varanasi — Ganga Aarti, Subah-e-Banaras, boat rides, BHU campus, and more.',
        'varanasi-solo-female-travelers-safety-travel-guide' => 'Is Varanasi safe for solo female travellers? Honest safety guide with practical tips, best areas to stay, and navigating the Ghats.',
        'best-time-to-visit-varanasi-month-by-month-guide'   => 'Best time to visit Varanasi — month by month guide covering weather, festivals, crowds, and planning tips for every season.',
    ];

    $slug = '';
    if (is_front_page()) {
        $slug = 'home';
    } elseif (is_singular()) {
        $slug = get_post_field('post_name', get_the_ID());
    } elseif (is_page()) {
        $slug = get_post_field('post_name', get_queried_object_id());
    }

    if ($slug && isset($descriptions[$slug])) {
        echo '<meta name=\"description\" content=\"' . esc_attr($descriptions[$slug]) . '\">' . \"
\";
        echo '<meta property=\"og:description\" content=\"' . esc_attr($descriptions[$slug]) . '\">' . \"
\";
    }

    // OG title and site name
    $title = is_front_page() ? 'Mosaic Hostel Varanasi — Near Assi Ghat' : wp_title('', false);
    echo '<meta property=\"og:title\" content=\"' . esc_attr($title) . '\">' . \"
\";
    echo '<meta property=\"og:site_name\" content=\"Mosaic Hostel Varanasi\">' . \"
\";
    echo '<meta property=\"og:type\" content=\"' . (is_single() ? 'article' : 'website') . '\">' . \"
\";
    echo '<meta property=\"og:url\" content=\"' . esc_url(get_permalink() ?: home_url('/')) . '\">' . \"
\";
    echo '<meta property=\"og:image\" content=\"https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp\">' . \"
\";
}, 1);

// 3. CANONICAL TAGS
add_action('wp_head', function() {
    if (is_front_page()) {
        $url = 'https://www.mosaichostels.com/';
    } elseif (is_singular()) {
        $url = get_permalink();
    } elseif (is_page()) {
        $url = get_permalink(get_queried_object_id());
    } else {
        return;
    }
    echo '<link rel=\"canonical\" href=\"' . esc_url($url) . '\">' . \"
\";
}, 2);

// 4. LODGING BUSINESS SCHEMA — Homepage
add_action('wp_head', function() {
    if (!is_front_page()) return;
    $schema = [
        '@context' => 'https://schema.org',
        '@type'    => 'LodgingBusiness',
        'name'     => 'Mosaic Hostel Varanasi',
        'url'      => 'https://www.mosaichostels.com',
        'telephone'=> '+919125492225',
        'email'    => 'hello@mosaichostels.com',
        'description' => 'Affordable community hostel near Assi Ghat, Varanasi. Private rooms and dorms with rooftop, 24-hour reception, AC, and WiFi. Rated 4.9★.',
        'address'  => [
            '@type'           => 'PostalAddress',
            'streetAddress'   => 'B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur',
            'addressLocality' => 'Varanasi',
            'addressRegion'   => 'Uttar Pradesh',
            'postalCode'      => '221005',
            'addressCountry'  => 'IN',
        ],
        'geo' => [
            '@type'     => 'GeoCoordinates',
            'latitude'  => 25.2808,
            'longitude' => 82.9979,
        ],
        'aggregateRating' => [
            '@type'       => 'AggregateRating',
            'ratingValue' => '4.9',
            'bestRating'  => '5',
            'worstRating' => '1',
            'ratingCount' => '500',
        ],
        'checkinTime'  => 'T13:00',
        'checkoutTime' => 'T10:30',
        'priceRange'   => '₹₹',
        'amenityFeature' => [
            ['@type'=>'LocationFeatureSpecification','name'=>'Free WiFi','value'=>true],
            ['@type'=>'LocationFeatureSpecification','name'=>'Air Conditioning','value'=>true],
            ['@type'=>'LocationFeatureSpecification','name'=>'24-Hour Reception','value'=>true],
            ['@type'=>'LocationFeatureSpecification','name'=>'Lockers','value'=>true],
            ['@type'=>'LocationFeatureSpecification','name'=>'Rooftop','value'=>true],
            ['@type'=>'LocationFeatureSpecification','name'=>'Common Room','value'=>true],
        ],
        'sameAs' => ['https://www.instagram.com/mosaichostels'],
        'openingHoursSpecification' => [
            '@type'      => 'OpeningHoursSpecification',
            'dayOfWeek'  => ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
            'opens'      => '00:00',
            'closes'     => '23:59',
        ],
        'image' => 'https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp',
    ];
    echo '<script type=\"application/ld+json\">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>' . \"
\";
}, 5);

// 5. ORGANIZATION SCHEMA — Homepage
add_action('wp_head', function() {
    if (!is_front_page()) return;
    $schema = [
        '@context' => 'https://schema.org',
        '@type'    => 'Organization',
        'name'     => 'Mosaic Hostel Varanasi',
        'url'      => 'https://www.mosaichostels.com',
        'logo'     => 'https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp',
        'contactPoint' => [
            '@type'           => 'ContactPoint',
            'telephone'       => '+919125492225',
            'contactType'     => 'reservations',
            'availableLanguage' => ['English','Hindi'],
        ],
        'sameAs' => ['https://www.instagram.com/mosaichostels'],
    ];
    echo '<script type=\"application/ld+json\">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>' . \"
\";
}, 6);

// 6. BLOGPOSTING SCHEMA — Single blog posts
add_action('wp_head', function() {
    if (!is_single()) return;
    $post    = get_post();
    $thumb   = get_the_post_thumbnail_url(null, 'large');
    $schema  = [
        '@context'        => 'https://schema.org',
        '@type'           => 'BlogPosting',
        'headline'        => get_the_title(),
        'url'             => get_permalink(),
        'datePublished'   => get_the_date('c'),
        'dateModified'    => get_the_modified_date('c'),
        'author'          => [
            '@type' => 'Organization',
            'name'  => 'Mosaic Hostel Team',
            'url'   => 'https://www.mosaichostels.com/about/',
        ],
        'publisher' => [
            '@type' => 'Organization',
            'name'  => 'Mosaic Hostel Varanasi',
            'url'   => 'https://www.mosaichostels.com',
            'logo'  => ['@type'=>'ImageObject','url'=>'https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp'],
        ],
        'image'           => ['@type'=>'ImageObject','url'=> $thumb ?: 'https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp'],
        'description'     => wp_strip_all_tags(get_the_excerpt()),
        'mainEntityOfPage'=> ['@type'=>'WebPage','@id'=>get_permalink()],
        'inLanguage'      => 'en',
        'about'           => ['@type'=>'Place','name'=>'Varanasi, Uttar Pradesh, India'],
    ];
    echo '<script type=\"application/ld+json\">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>' . \"
\";
}, 5);

// 7. LOCAL BUSINESS SCHEMA — Contact page
add_action('wp_head', function() {
    global $post;
    if (!is_page() || !$post || $post->post_name !== 'contact') return;
    $schema = [
        '@context' => 'https://schema.org',
        '@type'    => 'LodgingBusiness',
        'name'     => 'Mosaic Hostel Varanasi',
        'telephone'=> '+919125492225',
        'email'    => 'hello@mosaichostels.com',
        'address'  => [
            '@type'           => 'PostalAddress',
            'streetAddress'   => 'B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur',
            'addressLocality' => 'Varanasi',
            'addressRegion'   => 'Uttar Pradesh',
            'postalCode'      => '221005',
            'addressCountry'  => 'IN',
        ],
        'geo'   => ['@type'=>'GeoCoordinates','latitude'=>25.2808,'longitude'=>82.9979],
        'openingHoursSpecification' => [
            '@type'     => 'OpeningHoursSpecification',
            'dayOfWeek' => ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
            'opens'     => '00:00',
            'closes'    => '23:59',
        ],
        'url' => 'https://www.mosaichostels.com',
    ];
    echo '<script type=\"application/ld+json\">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>' . \"
\";
}, 5);

// 8. BREADCRUMB SCHEMA — Blog posts
add_action('wp_head', function() {
    if (!is_single()) return;
    $schema = [
        '@context'        => 'https://schema.org',
        '@type'           => 'BreadcrumbList',
        'itemListElement' => [
            ['@type'=>'ListItem','position'=>1,'name'=>'Home','item'=>'https://www.mosaichostels.com/'],
            ['@type'=>'ListItem','position'=>2,'name'=>'Blog','item'=>'https://www.mosaichostels.com/blog/'],
            ['@type'=>'ListItem','position'=>3,'name'=>get_the_title(),'item'=>get_permalink()],
        ],
    ];
    echo '<script type=\"application/ld+json\">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>' . \"
\";
}, 7);

// 9. ROBOTS.TXT — Add AI crawler permissions
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
    return $output;
}, 10, 2);

// 10. LLMS.TXT — Serve at /llms.txt
add_action('init', function() {
    add_rewrite_rule('^llms\.txt$', 'index.php?llms_txt=1', 'top');
});
add_filter('query_vars', function($vars) {
    $vars[] = 'llms_txt';
    return $vars;
});
add_action('template_redirect', function() {
    if (!get_query_var('llms_txt')) return;
    header('Content-Type: text/plain; charset=utf-8');
    echo \"# Mosaic Hostel Varanasi
\";
    echo \"> Affordable hostel near Assi Ghat, Varanasi, India. Est. 2025. Rated 4.9★ by 500+ guests.

\";
    echo \"## Key Pages

\";
    echo \"- [Home](https://www.mosaichostels.com/)
\";
    echo \"- [About Us](https://www.mosaichostels.com/about/)
\";
    echo \"- [Gallery](https://www.mosaichostels.com/gallery/)
\";
    echo \"- [Contact](https://www.mosaichostels.com/contact/)
\";
    echo \"- [Book Now](https://www.mosaichostels.com/book-now/)

\";
    echo \"## Blog — Varanasi Travel Guides

\";
    echo \"- [Best Hostels in Varanasi](https://www.mosaichostels.com/best-hostels-in-varanasi/)
\";
    echo \"- [Staying Near Assi Ghat — What to Expect](https://www.mosaichostels.com/hostel-near-assi-ghat-varanasi/)
\";
    echo \"- [Best Time to Visit Varanasi](https://www.mosaichostels.com/best-time-to-visit-varanasi-month-by-month-guide/)
\";
    echo \"- [Varanasi for Solo Female Travellers](https://www.mosaichostels.com/varanasi-solo-female-travelers-safety-travel-guide/)
\";
    echo \"- [Backpacker's Guide to Assi Ghat](https://www.mosaichostels.com/backpackers-guide-assi-ghat-varanasi/)
\";
    echo \"- [Why Assi Ghat is the Perfect Base](https://www.mosaichostels.com/why-assi-ghat-perfect-base-varanasi-stay/)
\";
    echo \"- [Top 7 Varanasi Experiences](https://www.mosaichostels.com/top-7-experiences-varanasi-traveler/)
\";
    echo \"- [7 Must-Do Experiences Near Mosaic Hostel](https://www.mosaichostels.com/7-must-do-experiences-near-mosaic-hostel-varanasi/)
\";
    echo \"- [10 Reasons Backpackers Love Mosaic Hostel](https://www.mosaichostels.com/10-reasons-backpackers-love-mosaic-hostel-varanasi/)

\";
    echo \"## NAP

\";
    echo \"**Address:** B1/85C, Assi Ghat Rd, Anandbagh, Bhelupur, Varanasi, Uttar Pradesh 221005, India
\";
    echo \"**Phone:** +91 91254 92225
\";
    echo \"**Email:** hello@mosaichostels.com
\";
    echo \"**Instagram:** https://www.instagram.com/mosaichostels
\";
    exit;
});
