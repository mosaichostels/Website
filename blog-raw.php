/* ── BLOG LISTING ── */
add_action('template_redirect', function() {

    /* single post */
    if (is_single() && get_post_type() === 'post') {
        $post = get_queried_object();
        setup_postdata($post);
        $title    = get_the_title($post);
        $content  = apply_filters('the_content', $post->post_content);
        $date     = get_the_date('F j, Y', $post);
        $cats     = get_the_category($post->ID);
        $cat_name = $cats ? esc_html($cats[0]->name) : 'Travel';
        $feat_url = get_the_post_thumbnail_url($post->ID, 'large') ?: 'https://www.mosaichostels.com/wp-content/uploads/2025/04/roshan-kmr-bsdXs-S4YFY-unsplash-2-scaled.jpg';
        $logo     = 'https://www.mosaichostels.com/wp-content/uploads/2025/08/Logo-Transperent.webp';
        $nav_html = mosaic_dynamic_nav('');

        while (ob_get_level()) ob_end_clean();
        header('Content-Type: text/html; charset=UTF-8');
        echo '<!DOCTYPE html><html lang=\"en\"><head>
<meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
<title>' . esc_html($title) . ' — Mosaic Hostel Varanasi</title>
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin><link rel=\"preload\" href=\"https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap\" as=\"style\" onload=\"this.onload=null;this.rel=\'stylesheet\'\"><noscript><link href=\"https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap\" rel=\"stylesheet\"></noscript>
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{--gold:#C8860A;--gold-lt:#E8B84B;--teal:#1A6B7A;--burg:#8B1A1A;--cobalt:#1A3A6B;--sage:#3D6B3A;--ink:#1A1208;--cream:#FAF4EA;--parch:#F2E8D5;--muted:#7A6A50;--border:rgba(200,134,10,0.15);}
html{scroll-behavior:smooth;}
body{background:var(--cream);color:var(--ink);font-family:\"Jost\",sans-serif;font-weight:300;overflow-x:hidden;cursor:none;}
#cursor{position:fixed;width:10px;height:10px;border-radius:50%;background:var(--gold);pointer-events:none;z-index:9999;transform:translate(-50%,-50%);mix-blend-mode:multiply;}
#cursor-ring{position:fixed;width:36px;height:36px;border-radius:50%;border:1px solid rgba(200,134,10,0.5);pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:left .08s,top .08s;}
#progress{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#C8860A,#8B1A1A,#1A6B7A);z-index:9999;width:0%;pointer-events:none;}
nav{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;align-items:center;justify-content:space-between;padding:0 64px;height:96px;background:rgba(250,244,234,0.97);border-bottom:1px solid var(--border);backdrop-filter:blur(20px);}
.nav-logo img{height:130px;width:auto;}
.nav-links{display:flex;gap:40px;}
.nav-links a{font-size:10px;letter-spacing:3.5px;text-transform:uppercase;color:var(--muted);text-decoration:none;padding-bottom:4px;position:relative;transition:color .25s;}
.nav-links a::after{content:\"\";position:absolute;bottom:0;left:0;right:100%;height:1px;background:var(--gold);transition:right .3s;}
.nav-links a:hover{color:var(--ink);}
.nav-links a:hover::after,.nav-links a.active::after{right:0;}
.nav-links a.active{color:var(--gold);}
.nav-book{padding:10px 28px;background:var(--gold);color:white;border:none;cursor:none;font-family:\"Jost\";font-size:10px;letter-spacing:4px;text-transform:uppercase;transition:background .25s;text-decoration:none;display:inline-block;}
.nav-book:hover{background:#A06E08;}
.post-hero{padding-top:96px;background:var(--ink);position:relative;overflow:hidden;}
.post-hero::before{content:\"\";position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,transparent,transparent 49px,rgba(200,134,10,0.04) 49px,rgba(200,134,10,0.04) 50px),repeating-linear-gradient(90deg,transparent,transparent 49px,rgba(200,134,10,0.04) 49px,rgba(200,134,10,0.04) 50px);}
.hero-img{position:relative;width:100%;height:440px;overflow:hidden;}
.hero-img img{width:100%;height:100%;object-fit:cover;opacity:0.45;}
.hero-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(26,18,8,0.95) 0%,rgba(26,18,8,0.4) 100%);}
.hero-text{position:absolute;bottom:0;left:0;right:0;padding:56px 120px;z-index:2;}
.hero-tag{font-size:9px;letter-spacing:6px;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}
.hero-title{font-family:\"Cinzel\",serif;font-size:44px;font-weight:400;color:white;letter-spacing:2px;line-height:1.15;max-width:700px;}
.hero-meta{margin-top:20px;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,0.4);}
.post-body{max-width:740px;margin:0 auto;padding:72px 40px 100px;}
.post-body h2{font-family:\"Cinzel\",serif;font-size:24px;font-weight:400;color:var(--ink);letter-spacing:1px;margin:48px 0 16px;padding-bottom:12px;border-bottom:1px solid var(--border);}
.post-body p{font-size:15px;color:#3A2E20;line-height:1.95;margin-bottom:20px;letter-spacing:0.15px;}
.post-body ul{margin:0 0 20px 20px;}
.post-body ul li{font-size:15px;color:#3A2E20;line-height:1.9;margin-bottom:8px;}
.post-body strong{color:var(--ink);font-weight:500;}
.tile-accent{display:flex;height:5px;}
.tile-accent span{flex:1;}
.post-cta{background:var(--ink);padding:72px 80px;text-align:center;position:relative;}
.post-cta-stripe{position:absolute;top:0;left:0;right:0;height:5px;display:flex;}
.post-cta-stripe span{flex:1;}
.post-cta-title{font-family:\"Cinzel\",serif;font-size:36px;color:white;letter-spacing:2px;margin-bottom:12px;}
.post-cta-sub{font-size:12px;letter-spacing:3px;color:rgba(255,255,255,0.35);text-transform:uppercase;margin-bottom:36px;}
.btn-gold{padding:14px 48px;background:var(--gold);color:white;font-family:\"Jost\";font-size:10px;letter-spacing:5px;text-transform:uppercase;border:none;cursor:none;text-decoration:none;display:inline-block;transition:background .3s;}
.btn-gold:hover{background:#A06E08;}
footer{background:#1A1208;padding:40px 80px 24px;}
.footer-bottom{display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(255,255,255,0.07);padding-top:16px;}
.footer-logo img{height:80px;width:auto;filter:brightness(0) invert(1);opacity:0.8;margin-bottom:16px;display:block;}
.footer-copy{font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:1px;}
.footer-strip{display:flex;gap:2px;width:60px;height:3px;}
.footer-strip span{flex:1;border-radius:1px;}



/* -- RESPONSIVE -- */
@media(hover:none),(pointer:coarse){body{cursor:auto;}#cursor,#cursor-ring{display:none!important;}a,button{cursor:pointer!important;}}
.nav-hamburger{display:none;flex-direction:column;justify-content:center;gap:5px;padding:10px;background:none;border:none;cursor:pointer;z-index:10001;flex-shrink:0;}
.nav-hamburger span{display:block;width:22px;height:1.5px;background:var(--ink);transition:transform .3s,opacity .3s;}
.nav-hamburger.open span:nth-child(1){transform:rotate(45deg) translate(4.5px,4.5px);}
.nav-hamburger.open span:nth-child(2){opacity:0;transform:translateX(-10px);}
.nav-hamburger.open span:nth-child(3){transform:rotate(-45deg) translate(4.5px,-4.5px);}
@media(max-width:1024px){
  nav{padding:0 32px;height:80px;justify-content:flex-start;}
  .nav-logo img{height:72px;}
  .nav-links{display:none;position:fixed;top:80px;left:0;right:0;bottom:0;z-index:9998;background:rgba(250,244,234,0.99);flex-direction:column;align-items:center;justify-content:center;gap:32px;backdrop-filter:none;-webkit-backdrop-filter:none;}
  .nav-links.open{display:flex;}
  .nav-links a{font-size:13px!important;letter-spacing:4px;color:var(--ink)!important;text-transform:uppercase;}
  .nav-hamburger{margin-left:auto;display:flex;}
  .nav-book{font-size:9px!important;padding:8px 14px!important;letter-spacing:3px;}
  .post-grid,.blog-grid{grid-template-columns:1fr 1fr;}
}
@media(max-width:767px){
  nav{
    padding:0 16px;height:60px;
    background:rgba(250,244,234,0.99)!important;
    backdrop-filter:none!important;-webkit-backdrop-filter:none!important;
    border-bottom:1px solid rgba(200,134,10,0.15)!important;
    transform:translateZ(0);-webkit-transform:translateZ(0);
  }
  .nav-logo img{height:52px;}
  .nav-links{top:60px;}
  .post-grid,.blog-grid{grid-template-columns:1fr;}
  .featured-card,.post-card{grid-column:span 1!important;}
  
  
  .page-title,.post-hero-title{font-size:34px!important;letter-spacing:3px;}
  footer{padding:40px 16px 24px;}
  .footer-top{flex-direction:column;gap:24px;}.footer-links-wrap{flex-direction:column;gap:16px;}
}
@media(max-width:1024px){
  .post-cta{padding:60px 40px;}
  .post-cta-title{font-size:28px;}
  footer{padding:40px 40px 24px;}
  .post-content{padding:0 32px 60px;}
  .post-body{max-width:100%;}
}
@media(max-width:767px){
  .post-cta{padding:48px 16px;}
  .post-cta-title{font-size:24px;letter-spacing:1px;}
  footer{padding:40px 16px 24px;}
  .post-content{padding:0 16px 48px;}
  .featured-wrap{padding:40px 16px;}
  .feat-title{font-size:26px!important;letter-spacing:1px;}
  .posts-section{padding:40px 16px 60px;}
}

/* ── RESPONSIVE ADDITIONS ── */
@media(max-width:1024px){
  .post-cta{padding:60px 40px;}
  .post-cta-title{font-size:28px;}
  footer{padding:40px 40px 24px;}
}
@media(max-width:767px){
  .post-cta{padding:48px 16px;}
  .post-cta-title{font-size:24px;letter-spacing:1px;}
  footer{padding:40px 16px 24px;}
  .feat-title{font-size:26px!important;letter-spacing:1px;}
}
</style>' . (function_exists('mosaic_post_head_tags') ? mosaic_post_head_tags($title, $post, $feat_url, get_permalink($post->ID), get_the_excerpt($post->ID)) : '') . '</head><body>
<div id=\"cursor\"></div><div id=\"cursor-ring\"></div><div id=\"progress\"></div>';

        /* Nav */
        echo '<nav><div class=\"nav-logo\"><a href=\"' . home_url('/') . '\" style=\"display:block\"><img src=\"' . $logo . '\" alt=\"Mosaic Hostel\"></a></div><div class=\"nav-links\">';
        $menu_items = wp_get_nav_menu_items('main-menu');
        if ($menu_items) {
            foreach ($menu_items as $item) {
                if (strtolower(trim($item->title)) === 'book now') continue;
                $active = (strpos(rtrim($item->url,'/'), rtrim(home_url('/blog'),'/')) !== false) ? ' class=\"active\"' : '';
                echo '<a href=\"' . esc_url($item->url) . '\"' . $active . '>' . esc_html($item->title) . '</a>';
            }
        }
        echo '</div><button class=\"nav-hamburger\" id=\"navHam\" aria-label=\"Open menu\"><span></span><span></span><span></span></button><a href=\"' . home_url('/book-now/') . '\" class=\"nav-book\">Book Now</a></nav>';

        /* Hero */
        echo '<div class=\"post-hero\"><div class=\"hero-img\"><img src=\"' . esc_url($feat_url) . '\" alt=\"' . esc_attr($title) . ' — Mosaic Hostel Varanasi\"><div class=\"hero-overlay\"></div><div class=\"hero-text\"><div class=\"hero-tag\">' . $cat_name . '</div><h1 class=\"hero-title\">' . esc_html($title) . '</h1><div class=\"hero-meta\">Mosaic Hostel · ' . $date . '</div></div></div></div>';

        /* Tile strip */
        echo '<div class=\"tile-accent\" id=\"div0\"></div>';

        /* Content */
        echo '<div class=\"post-body\">' . $content . '</div>';

        /* CTA */
        echo '<div class=\"post-cta\"><div class=\"post-cta-stripe\" id=\"ctaStripe\"></div><div class=\"post-cta-title\">Stay at Mosaic Hostel</div><div class=\"post-cta-sub\">Near Assi Ghat · Varanasi · Est. 2019</div><a class=\"btn-gold\" href=\"' . home_url('/book-now/') . '\">Book Your Stay</a></div>';

        /* Footer */
        echo '<footer><div class=\"footer-logo\"><img src=\"' . $logo . '\" alt=\"Mosaic Hostel\"></div><div class=\"footer-bottom\"><div class=\"footer-copy\">&copy; 2025 Mosaic Hostel Varanasi.</div><div class=\"footer-strip\" id=\"footerStrip\"></div><div class=\"footer-copy\">Made with &hearts; in Varanasi</div></div></footer>';

        /* JS */
        echo '<script>
const LC=[\"#C8860A\",\"#8B1A1A\",\"#1A6B7A\",\"#1A3A6B\",\"#5C3A1E\",\"#E8B84B\",\"#3D6B3A\",\"#A02020\",\"#2D9AAA\",\"#7A4F2A\"];
function pick(a){return a[Math.floor(Math.random()*a.length)];}
function fill(el,cols){if(!el)return;cols.forEach(c=>{const s=document.createElement(\"span\");s.style.flex=\"1\";s.style.background=c;el.appendChild(s);});}
fill(document.getElementById(\"div0\"),LC);
fill(document.getElementById(\"ctaStripe\"),[...LC,...LC]);
fill(document.getElementById(\"footerStrip\"),[\"#C8860A\",\"#8B1A1A\",\"#1A6B7A\",\"#1A3A6B\",\"#3D6B3A\"]);
const cur=document.getElementById(\"cursor\"),ring=document.getElementById(\"cursor-ring\");
document.addEventListener(\"mousemove\",e=>{cur.style.left=e.clientX+\"px\";cur.style.top=e.clientY+\"px\";ring.style.left=e.clientX+\"px\";ring.style.top=e.clientY+\"px\";});
window.addEventListener(\"scroll\",()=>{document.getElementById(\"progress\").style.width=((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100)+\"%\";},{passive:true});


(function(){
  var ham=document.getElementById(\"navHam\");
  var nl=document.querySelector(\".nav-links\");
  if(!ham||!nl)return;
  ham.addEventListener(\"click\",function(){
    nl.classList.toggle(\"open\");ham.classList.toggle(\"open\");
    document.body.style.overflow=nl.classList.contains(\"open\")?\"hidden\":\"\";
  });
  nl.querySelectorAll(\"a\").forEach(function(a){
    a.addEventListener(\"click\",function(){
      nl.classList.remove(\"open\");ham.classList.remove(\"open\");
      document.body.style.overflow=\"\";
    });
  });
})();
</script></body></html>';
        exit;
    }

    /* blog listing */
    if (is_page('blog') || is_home()) {
        $logo  = 'https://www.mosaichostels.com/wp-content/uploads/2025/08/Logo-Transperent.webp';
        $query = new WP_Query(['post_type'=>'post','posts_per_page'=>20,'post_status'=>'publish','orderby'=>'date','order'=>'DESC']);
        $posts = $query->posts;

        while (ob_get_level()) ob_end_clean();
        header('Content-Type: text/html; charset=UTF-8');

        $lc = '[\"#C8860A\",\"#8B1A1A\",\"#1A6B7A\",\"#1A3A6B\",\"#5C3A1E\",\"#E8B84B\",\"#3D6B3A\",\"#A02020\",\"#2D9AAA\",\"#7A4F2A\"]';
        $pals = ['gold'=>'[\"#C8860A\",\"#E8B84B\",\"#D4930F\"]','teal'=>'[\"#1A6B7A\",\"#2D9AAA\"]','burg'=>'[\"#8B1A1A\",\"#A02020\"]','cobalt'=>'[\"#1A3A6B\",\"#2A5A9B\"]','sage'=>'[\"#3D6B3A\",\"#2D5A2A\"]'];
        $pal_keys = array_keys($pals);

        echo mosaic_dynamic_nav('<!DOCTYPE html><html lang=\"en\"><head>
<meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
<title>Blog — Mosaic Hostel Varanasi</title>
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin><link rel=\"preload\" href=\"https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap\" as=\"style\" onload=\"this.onload=null;this.rel=\'stylesheet\'\"><noscript><link href=\"https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Jost:wght@200;300;400;500&display=swap\" rel=\"stylesheet\"></noscript>
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{--gold:#C8860A;--gold-lt:#E8B84B;--teal:#1A6B7A;--burg:#8B1A1A;--cobalt:#1A3A6B;--sage:#3D6B3A;--ink:#1A1208;--cream:#FAF4EA;--parch:#F2E8D5;--muted:#7A6A50;--border:rgba(200,134,10,0.15);}
html{scroll-behavior:smooth;}
body{background:var(--cream);color:var(--ink);font-family:\"Jost\",sans-serif;font-weight:300;overflow-x:hidden;cursor:none;}
#cursor{position:fixed;width:10px;height:10px;border-radius:50%;background:var(--gold);pointer-events:none;z-index:9999;transform:translate(-50%,-50%);mix-blend-mode:multiply;}
#cursor-ring{position:fixed;width:36px;height:36px;border-radius:50%;border:1px solid rgba(200,134,10,0.5);pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:left .08s,top .08s;}
#progress{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#C8860A,#8B1A1A,#1A6B7A);z-index:9999;width:0%;pointer-events:none;}
.tile-accent{display:flex;height:5px;}.tile-accent span{flex:1;}
nav{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;align-items:center;justify-content:space-between;padding:0 64px;height:96px;background:rgba(250,244,234,0.97);border-bottom:1px solid var(--border);backdrop-filter:blur(20px);}
.nav-logo img{height:130px;width:auto;}.nav-links{display:flex;gap:40px;}
.nav-links a{font-size:10px;letter-spacing:3.5px;text-transform:uppercase;color:var(--muted);text-decoration:none;padding-bottom:4px;position:relative;transition:color .25s;}
.nav-links a::after{content:\"\";position:absolute;bottom:0;left:0;right:100%;height:1px;background:var(--gold);transition:right .3s;}
.nav-links a:hover{color:var(--ink);}.nav-links a:hover::after,.nav-links a.active::after{right:0;}.nav-links a.active{color:var(--gold);}
.nav-book{padding:10px 28px;background:var(--gold);color:white;border:none;cursor:none;font-family:\"Jost\";font-size:10px;letter-spacing:4px;text-transform:uppercase;transition:background .25s;text-decoration:none;display:inline-block;}
.nav-book:hover{background:#A06E08;}
.page-hero{padding-top:96px;background:var(--ink);position:relative;overflow:hidden;text-align:center;padding-bottom:80px;}
.page-hero::before{content:\"\";position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,transparent,transparent 49px,rgba(200,134,10,0.04) 49px,rgba(200,134,10,0.04) 50px),repeating-linear-gradient(90deg,transparent,transparent 49px,rgba(200,134,10,0.04) 49px,rgba(200,134,10,0.04) 50px);}
.hero-stripe{position:absolute;top:96px;left:0;right:0;height:5px;display:flex;}.hero-stripe span{flex:1;}
.hero-content{position:relative;z-index:1;padding:72px 24px 0;}
.page-eyebrow{font-size:10px;letter-spacing:7px;text-transform:uppercase;color:var(--gold);margin-bottom:20px;}
.page-title{font-family:\"Cinzel\",serif;font-size:64px;font-weight:400;color:white;letter-spacing:6px;line-height:1;margin-bottom:16px;}
.page-sub{font-size:14px;font-weight:300;letter-spacing:2px;color:rgba(255,255,255,0.45);}
.featured-wrap{max-width:1200px;margin:-56px auto 0;padding:0 80px;position:relative;z-index:5;}
.featured-card{display:grid;grid-template-columns:1.4fr 1fr;background:white;border:1px solid var(--border);overflow:hidden;box-shadow:0 20px 60px rgba(26,18,8,0.1);text-decoration:none;color:inherit;transition:box-shadow .3s;cursor:none;}
.featured-card:hover{box-shadow:0 24px 80px rgba(26,18,8,0.15);}
.featured-photo-wrap{position:relative;overflow:hidden;min-height:400px;}
.featured-photo{width:100%;height:100%;object-fit:cover;transition:transform .6s;}
.featured-card:hover .featured-photo{transform:scale(1.04);}
.feat-acc{position:absolute;top:0;left:0;right:0;height:4px;display:flex;}
.feat-acc span{flex:1;}
.feat-tag{position:absolute;top:24px;left:24px;padding:6px 16px;background:var(--gold);color:white;font-size:9px;letter-spacing:5px;text-transform:uppercase;}
.feat-text{padding:52px;display:flex;flex-direction:column;justify-content:center;}
.feat-label{font-size:9px;letter-spacing:5px;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}
.feat-title{font-family:\"Cinzel\",serif;font-size:28px;font-weight:400;color:var(--ink);letter-spacing:1px;line-height:1.2;margin-bottom:16px;}
.feat-tline{display:flex;gap:2px;height:3px;width:60px;margin-bottom:16px;}.feat-tline span{flex:1;border-radius:1px;}
.feat-excerpt{font-size:14px;color:var(--muted);line-height:1.85;margin-bottom:24px;}
.feat-meta{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);}
.read-more{display:inline-flex;align-items:center;gap:10px;font-size:10px;letter-spacing:4px;text-transform:uppercase;color:var(--gold);margin-top:24px;transition:gap .25s;}
.read-more:hover{gap:18px;}.read-more::after{content:\"→\";}
.posts-section{max-width:1200px;margin:0 auto;padding:80px 80px 100px;}
.posts-hdr{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:48px;}
.posts-hdr-title{font-family:\"Cinzel\",serif;font-size:28px;font-weight:400;color:var(--ink);letter-spacing:2px;}
.posts-count{font-size:10px;letter-spacing:4px;text-transform:uppercase;color:var(--muted);}
.posts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;}
.post-card{background:white;border:1px solid var(--border);overflow:hidden;cursor:none;transition:transform .3s,box-shadow .3s;text-decoration:none;color:inherit;display:flex;flex-direction:column;}
.post-card:hover{transform:translateY(-4px);box-shadow:0 16px 48px rgba(200,134,10,0.1);}
.pc-photo-wrap{position:relative;overflow:hidden;height:220px;}
.pc-photo{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
.post-card:hover .pc-photo{transform:scale(1.06);}
.pc-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(26,18,8,0.4) 0%,transparent 60%);opacity:0;transition:opacity .3s;}
.post-card:hover .pc-overlay{opacity:1;}
.pc-acc{position:absolute;top:0;left:0;right:0;height:4px;display:flex;gap:1px;transform:scaleX(0);transform-origin:left;transition:transform .4s;}
.post-card:hover .pc-acc{transform:scaleX(1);}.pc-acc span{flex:1;}
.pc-body{padding:28px;flex:1;display:flex;flex-direction:column;}
.pc-tag{font-size:9px;letter-spacing:5px;text-transform:uppercase;color:var(--gold);margin-bottom:12px;}
.pc-title{font-family:\"Cinzel\",serif;font-size:17px;font-weight:400;color:var(--ink);letter-spacing:.5px;line-height:1.3;margin-bottom:12px;}
.pc-excerpt{font-size:13px;color:var(--muted);line-height:1.8;flex:1;}
.pc-foot{display:flex;justify-content:space-between;align-items:center;margin-top:20px;padding-top:16px;border-top:1px solid var(--border);}
.pc-date{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);}
.pc-arrow{font-size:14px;color:var(--gold);transition:transform .25s;}
.post-card:hover .pc-arrow{transform:translateX(4px);}









footer{background:#1A1208;padding:48px 80px 28px;}
.ft-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:40px;}
.ft-logo img{height:110px;width:auto;filter:brightness(0) invert(1);opacity:0.9;}
.ft-links{display:flex;gap:64px;}
.ft-col h4{font-size:9px;letter-spacing:5px;text-transform:uppercase;color:var(--gold);margin-bottom:18px;}
.ft-col a{display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;transition:color .2s;}
.ft-col a:hover{color:white;}
.ft-bot{border-top:1px solid rgba(255,255,255,0.07);padding-top:20px;display:flex;justify-content:space-between;align-items:center;}
.ft-copy{font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:1px;}
.ft-strip{display:flex;gap:2px;width:80px;height:4px;}.ft-strip span{flex:1;border-radius:1px;}
.reveal{opacity:0;transform:translateY(24px);transition:opacity .7s ease,transform .7s ease;}.reveal.visible{opacity:1;transform:none;}
.reveal-d1{transition-delay:.1s;}.reveal-d2{transition-delay:.2s;}.reveal-d3{transition-delay:.3s;}



/* -- RESPONSIVE -- */
@media(hover:none),(pointer:coarse){body{cursor:auto;}#cursor,#cursor-ring{display:none!important;}a,button{cursor:pointer!important;}}
.nav-hamburger{display:none;flex-direction:column;justify-content:center;gap:5px;padding:10px;background:none;border:none;cursor:pointer;z-index:10001;flex-shrink:0;}
.nav-hamburger span{display:block;width:22px;height:1.5px;background:var(--ink);transition:transform .3s,opacity .3s;}
.nav-hamburger.open span:nth-child(1){transform:rotate(45deg) translate(4.5px,4.5px);}
.nav-hamburger.open span:nth-child(2){opacity:0;transform:translateX(-10px);}
.nav-hamburger.open span:nth-child(3){transform:rotate(-45deg) translate(4.5px,-4.5px);}
@media(max-width:1024px){
  nav{padding:0 32px;height:80px;justify-content:flex-start;}
  .nav-logo img{height:72px;}
  .nav-links{display:none;position:fixed;top:80px;left:0;right:0;bottom:0;z-index:9998;background:rgba(250,244,234,0.99);flex-direction:column;align-items:center;justify-content:center;gap:32px;backdrop-filter:none;-webkit-backdrop-filter:none;}
  .nav-links.open{display:flex;}
  .nav-links a{font-size:13px!important;letter-spacing:4px;color:var(--ink)!important;text-transform:uppercase;}
  .nav-hamburger{margin-left:auto;display:flex;}
  .nav-book{font-size:9px!important;padding:8px 14px!important;letter-spacing:3px;}
  .post-grid,.blog-grid{grid-template-columns:1fr 1fr;}
}
@media(max-width:767px){
  nav{
    padding:0 16px;height:60px;
    background:rgba(250,244,234,0.99)!important;
    backdrop-filter:none!important;-webkit-backdrop-filter:none!important;
    border-bottom:1px solid rgba(200,134,10,0.15)!important;
    transform:translateZ(0);-webkit-transform:translateZ(0);
  }
  .nav-logo img{height:52px;}
  .nav-links{top:60px;}
  .post-grid,.blog-grid{grid-template-columns:1fr;}
  .featured-card,.post-card{grid-column:span 1!important;}
  
  
  .page-title,.post-hero-title{font-size:34px!important;letter-spacing:3px;}
  footer{padding:40px 16px 24px;}
  .footer-top{flex-direction:column;gap:24px;}.footer-links-wrap{flex-direction:column;gap:16px;}
}

/* ── RESPONSIVE ADDITIONS (LISTING) ── */
@media(max-width:1024px){
  footer{padding:40px 40px 24px;}
}
@media(max-width:767px){
  footer{padding:40px 16px 24px;}
  .feat-title{font-size:26px!important;letter-spacing:1px;}
  .featured-wrap{padding:40px 16px;}
}

/* ── MOBILE RESPONSIVE v2 ── */
@media(max-width:1024px){.page-title{font-size:46px!important;letter-spacing:4px!important;}.posts-section{padding:60px 40px 80px!important;}.featured-wrap{padding:0 40px!important;}.feat-title{font-size:24px!important;}}
@media(max-width:767px){.posts-section{padding:40px 16px 60px!important;}.blog-grid{grid-template-columns:1fr!important;}.post-card{grid-column:span 1!important;}}
</style>' . (function_exists('mosaic_page_head_tags') ? mosaic_page_head_tags('blog') : '') . '</head><body>
<div id=\"cursor\"></div><div id=\"cursor-ring\"></div><div id=\"progress\"></div>
<!-- NAV_PLACEHOLDER -->');

        /* Nav */
        echo '<nav><div class=\"nav-logo\"><a href=\"' . home_url('/') . '\" style=\"display:block\"><img src=\"' . $logo . '\" alt=\"Mosaic Hostel\"></a></div><div class=\"nav-links\">';
        $menu_items = wp_get_nav_menu_items('main-menu');
        $book_url = home_url('/book-now/');
        if ($menu_items) {
            foreach ($menu_items as $mi) {
                if (strtolower(trim($mi->title)) === 'book now') { $book_url = $mi->url; continue; }
                $is_blog = (strpos(rtrim($mi->url,'/'), rtrim(home_url('/blog'),'/')) !== false);
                $active = $is_blog ? ' class=\"active\"' : '';
                echo '<a href=\"' . esc_url($mi->url) . '\"' . $active . '>' . esc_html($mi->title) . '</a>';
            }
        }
        echo '</div><button class=\"nav-hamburger\" id=\"navHam\" aria-label=\"Open menu\"><span></span><span></span><span></span></button><a href=\"' . esc_url($book_url) . '\" class=\"nav-book\">Book Now</a></nav>';

        /* Hero */
        echo '<div class=\"page-hero\"><div class=\"hero-stripe\" id=\"hs\"></div><div class=\"hero-content\"><div class=\"page-eyebrow\">Varanasi Stories</div><h1 class=\"page-title\">The Blog</h1><div class=\"page-sub\">Travel guides, hostel tips &amp; the spirit of Varanasi</div></div></div>';
        echo '<div class=\"tile-accent\" id=\"div0\"></div>';

        /* Featured (first post) */
        if (!empty($posts)) {
            $fp    = $posts[0];
            $fp_url = get_permalink($fp->ID);
            $fp_img = get_the_post_thumbnail_url($fp->ID,'large') ?: '';
            $fp_cats = get_the_category($fp->ID);
            $fp_cat = $fp_cats ? esc_html($fp_cats[0]->name) : 'Guide';
            $fp_exc = wp_trim_words(get_the_excerpt($fp->ID) ?: strip_tags($fp->post_content), 32);
            echo '<div class=\"featured-wrap reveal\"><a class=\"featured-card\" href=\"' . esc_url($fp_url) . '\">';
            echo '<div class=\"featured-photo-wrap\"><div class=\"feat-acc\" id=\"fa\"></div>';
            if ($fp_img) echo '<img class=\"featured-photo\" src=\"' . esc_url($fp_img) . '\" alt=\"' . esc_attr($p->post_title) . ' — Mosaic Hostel Varanasi\">';
            echo '<div class=\"feat-tag\">Featured</div></div>';
            echo '<div class=\"feat-text\"><div class=\"feat-label\">' . $fp_cat . '</div>';
            echo '<div class=\"feat-title\">' . esc_html(get_the_title($fp->ID)) . '</div>';
            echo '<div class=\"feat-tline\" id=\"ftl\"></div>';
            echo '<div class=\"feat-excerpt\">' . esc_html($fp_exc) . '</div>';
            echo '<div class=\"feat-meta\">' . $fp_cat . ' · ' . get_the_date('F Y', $fp->ID) . '</div>';
            echo '<div class=\"read-more\">Read Article</div></div></a></div>';
        }

        /* Grid (remaining posts) */
        $remaining = array_slice($posts, 1);
        echo '<div class=\"posts-section\"><div class=\"posts-hdr\"><div class=\"posts-hdr-title\">All Articles</div><div class=\"posts-count\">' . count($posts) . ' Articles</div></div><div class=\"posts-grid\">';
        $pal_list = array_keys($pals);
        foreach ($remaining as $i => $p) {
            $p_url = get_permalink($p->ID);
            $p_img = get_the_post_thumbnail_url($p->ID,'medium_large') ?: '';
            $p_cats = get_the_category($p->ID);
            $p_cat = $p_cats ? esc_html($p_cats[0]->name) : 'Guide';
            $p_exc = wp_trim_words(get_the_excerpt($p->ID) ?: strip_tags($p->post_content), 22);
            $p_date = get_the_date('M Y', $p->ID);
            $pal_key = $pal_list[$i % count($pal_list)];
            $delay_class = $i % 3 === 1 ? ' reveal-d1' : ($i % 3 === 2 ? ' reveal-d2' : '');
            echo '<a class=\"post-card reveal' . $delay_class . '\" href=\"' . esc_url($p_url) . '\">';
            echo '<div class=\"pc-photo-wrap\"><div class=\"pc-acc\" data-pal=\"' . $pal_key . '\"></div>';
            if ($p_img) echo '<img class=\"pc-photo\" src=\"' . esc_url($p_img) . '\" alt=\"' . esc_attr($p->post_title) . '\" loading=\"lazy\">';
            echo '<div class=\"pc-overlay\"></div></div>';
            echo '<div class=\"pc-body\"><div class=\"pc-tag\">' . $p_cat . '</div><div class=\"pc-title\">' . esc_html(get_the_title($p->ID)) . '</div><div class=\"pc-excerpt\">' . esc_html($p_exc) . '</div>';
            echo '<div class=\"pc-foot\"><div class=\"pc-date\">' . $p_date . '</div><div class=\"pc-arrow\">→</div></div></div></a>';
        }
        echo '</div></div>';

        /* Newsletter */
        echo '<div class=\"tile-accent\" id=\"div1\"></div>';

        /* Footer */
        echo '<footer><div class=\"ft-top\"><div class=\"ft-logo\"><img src=\"' . $logo . '\" alt=\"Mosaic Hostel\"></div><div class=\"ft-links\"><div class=\"ft-col\"><h4>Stay</h4><a href=\"#\">Private Room</a><a href=\"#\">8-Bed Mixed Dorm</a><a href=\"#\">6-Bed Mixed Dorm</a><a href=\"#\">4-Bed Mixed Dorm</a><a href=\"#\">6-Bed Female Dorm</a></div><div class=\"ft-col\"><h4>Explore</h4><a href=\"' . home_url('/gallery/') . '\">Gallery</a><a href=\"' . home_url('/about/') . '\">About Us</a><a href=\"' . home_url('/blog/') . '\">Blog</a><a href=\"' . home_url('/contact/') . '\">Contact</a></div><div class=\"ft-col\"><h4>Connect</h4><a href=\"https://wa.me/919125492225\" target=\"_blank\">WhatsApp</a><a href=\"mailto:mosaichostels@gmail.com\">Email Us</a><a href=\"https://www.instagram.com/mosaichostels\" target=\"_blank\">Instagram</a></div></div></div><div class=\"ft-bot\"><div class=\"ft-copy\">&copy; 2025 Mosaic Hostel Varanasi. All rights reserved.</div><div class=\"ft-strip\" id=\"fs\"></div><div class=\"ft-copy\">Made with &hearts; in Varanasi</div></div></footer>';

        /* JS */
        echo '<script>
const LC=' . $lc . ';
const PALS={gold:[\"#C8860A\",\"#E8B84B\",\"#D4930F\"],teal:[\"#1A6B7A\",\"#2D9AAA\"],burg:[\"#8B1A1A\",\"#A02020\"],cobalt:[\"#1A3A6B\",\"#2A5A9B\"],sage:[\"#3D6B3A\",\"#2D5A2A\"]};
function pick(a){return a[Math.floor(Math.random()*a.length)];}
function fill(el,cols){if(!el)return;cols.forEach(c=>{const s=document.createElement(\"span\");s.style.flex=\"1\";s.style.background=c;el.appendChild(s);});}
function fillId(id,cols){fill(document.getElementById(id),cols);}
fillId(\"hs\",LC);fillId(\"div0\",LC);fillId(\"div1\",LC);fillId(\"div2\",LC);fillId(\"fs\",[\"#C8860A\",\"#8B1A1A\",\"#1A6B7A\",\"#1A3A6B\",\"#3D6B3A\"]);
if(document.getElementById(\"fa\")){fill(document.getElementById(\"fa\"),LC);}
if(document.getElementById(\"ftl\")){fill(document.getElementById(\"ftl\"),[\"#C8860A\",\"#8B1A1A\",\"#1A6B7A\",\"#1A3A6B\",\"#3D6B3A\"]);}
document.querySelectorAll(\".pc-acc\").forEach(el=>{const pal=PALS[el.dataset.pal]||LC;for(let i=0;i<20;i++){const s=document.createElement(\"span\");s.style.flex=\"1\";s.style.background=pick(pal);el.appendChild(s);}});
const cur=document.getElementById(\"cursor\"),ring=document.getElementById(\"cursor-ring\");
document.addEventListener(\"mousemove\",e=>{cur.style.left=e.clientX+\"px\";cur.style.top=e.clientY+\"px\";ring.style.left=e.clientX+\"px\";ring.style.top=e.clientY+\"px\";});
document.querySelectorAll(\"a,button,input\").forEach(el=>{el.addEventListener(\"mouseenter\",()=>{cur.style.width=\"18px\";cur.style.height=\"18px\";ring.style.width=\"48px\";ring.style.height=\"48px\";});el.addEventListener(\"mouseleave\",()=>{cur.style.width=\"10px\";cur.style.height=\"10px\";ring.style.width=\"36px\";ring.style.height=\"36px\";});});
window.addEventListener(\"scroll\",()=>{document.getElementById(\"progress\").style.width=((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100)+\"%\";},{passive:true});
const obs=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add(\"visible\");});},{threshold:0.08});
document.querySelectorAll(\".reveal\").forEach(el=>obs.observe(el));


(function(){
  var ham=document.getElementById(\"navHam\");
  var nl=document.querySelector(\".nav-links\");
  if(!ham||!nl)return;
  ham.addEventListener(\"click\",function(){
    nl.classList.toggle(\"open\");ham.classList.toggle(\"open\");
    document.body.style.overflow=nl.classList.contains(\"open\")?\"hidden\":\"\";
  });
  nl.querySelectorAll(\"a\").forEach(function(a){
    a.addEventListener(\"click\",function(){
      nl.classList.remove(\"open\");ham.classList.remove(\"open\");
      document.body.style.overflow=\"\";
    });
  });
})();
</script></body></html>';
        exit;
    }
}, 2);

