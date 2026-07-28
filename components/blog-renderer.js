// ── MARKDOWN RENDERING UTILITIES ──
// Client-side markdown to HTML conversion for blog system

/**
 * Fetch a markdown file by slug
 * @param {string} slug - Blog post slug (filename without .md)
 * @returns {Promise<string>} Markdown content
 */
async function loadMarkdownFile(slug) {
  const relativeUrl = `/blogs/${slug}.md`;
  const absoluteUrl = window.location.origin + relativeUrl;

  console.log(`[loadMarkdownFile] Starting fetch for slug: ${slug}`);
  console.log(`[loadMarkdownFile] Relative URL: ${relativeUrl}`);
  console.log(`[loadMarkdownFile] Absolute URL: ${absoluteUrl}`);
  console.log(`[loadMarkdownFile] Origin: ${window.location.origin}`);
  console.log(`[loadMarkdownFile] Protocol: ${window.location.protocol}`);

  try {
    // Try absolute URL first (more reliable in Safari)
    console.log(`[loadMarkdownFile] Calling fetch with absolute URL...`);
    const response = await fetch(absoluteUrl);
    console.log(`[loadMarkdownFile] Fetch returned, status: ${response.status} ${response.statusText}`);
    console.log(`[loadMarkdownFile] Response OK: ${response.ok}`);
    console.log(`[loadMarkdownFile] Response type: ${response.type}`);
    console.log(`[loadMarkdownFile] Response url: ${response.url}`);

    if (!response.ok) {
      console.error(`[loadMarkdownFile] Response not OK! Throwing error.`);
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    console.log(`[loadMarkdownFile] Getting response text...`);
    const text = await response.text();
    console.log(`[loadMarkdownFile] Got text, length: ${text.length} bytes`);
    console.log(`[loadMarkdownFile] First 100 chars: ${text.substring(0, 100)}`);
    return text;
  } catch (error) {
    console.error(`[loadMarkdownFile] Absolute URL fetch FAILED! Trying relative URL...`);
    console.error(`[loadMarkdownFile] Error:`, error.message);

    try {
      console.log(`[loadMarkdownFile] Retrying with relative URL: ${relativeUrl}`);
      const fallbackResponse = await fetch(relativeUrl);
      console.log(`[loadMarkdownFile] Fallback fetch succeeded, status: ${fallbackResponse.status}`);

      if (!fallbackResponse.ok) {
        throw new Error(`HTTP ${fallbackResponse.status}: ${fallbackResponse.statusText}`);
      }

      const text = await fallbackResponse.text();
      console.log(`[loadMarkdownFile] Got fallback text, length: ${text.length}`);
      return text;
    } catch (fallbackError) {
      console.error(`[loadMarkdownFile] BOTH FETCHES FAILED!`);
      console.error(`[loadMarkdownFile] Error type: ${error.constructor.name}`);
      console.error(`[loadMarkdownFile] Error message: ${error.message}`);
      console.error(`[loadMarkdownFile] Fallback error: ${fallbackError.message}`);
      console.error(`[loadMarkdownFile] Full error:`, error);
      console.error(`[loadMarkdownFile] Full fallback error:`, fallbackError);
      throw new Error(`Failed to load blog post "${slug}": ${error.message}; Fallback: ${fallbackError.message}`);
    }
  }
}

/**
 * Convert markdown string to HTML
 * @param {string} markdown - Markdown content
 * @returns {string} HTML
 */
function parseMarkdown(markdown) {
  if (typeof marked === 'undefined') {
    throw new Error('marked.js library not loaded');
  }
  try {
    return marked.parse(markdown);
  } catch (error) {
    console.error('Error parsing markdown:', error);
    throw new Error(`Markdown parsing failed: ${error.message}`);
  }
}

/**
 * Extract title from markdown (first H1)
 * @param {string} markdown - Markdown content
 * @param {string} fallback - Fallback if no H1 found
 * @returns {string} Title
 */
function extractTitle(markdown, fallback = 'Untitled') {
  const match = markdown.match(/^#\s+(.+?)$/m);
  return match ? match[1].trim() : fallback;
}

/**
 * Extract excerpt from markdown (first N characters)
 * @param {string} markdown - Markdown content
 * @param {number} length - Max length (default 150)
 * @returns {string} Excerpt
 */
function extractExcerpt(markdown, length = 150) {
  // Remove markdown syntax, get first N chars
  const text = markdown
    .replace(/^#+ .+$/gm, '') // Remove headers
    .replace(/\[(.+?)\]\(.+?\)/g, '$1') // Convert [text](url) → text
    .replace(/[*_`]/g, '') // Remove formatting
    .replace(/\n+/g, ' ') // Replace newlines with space
    .trim();

  return text.length > length
    ? text.substring(0, length) + '...'
    : text;
}

/**
 * Extract date from markdown (YAML frontmatter or inline format)
 * Supports: YAML frontmatter (---\ndate: YYYY-MM-DD\n---) OR inline (**Published:** YYYY-MM-DD HH:MM:SS)
 * @param {string} markdown - Markdown content
 * @returns {string} Date (YYYY-MM-DD format) or empty string
 */
function extractDate(markdown) {
  // Try YAML frontmatter first
  const frontmatterMatch = markdown.match(/^---\n([\s\S]+?)\n---/);
  if (frontmatterMatch) {
    const dateMatch = frontmatterMatch[1].match(/date:\s*(.+?)$/m);
    if (dateMatch) return dateMatch[1].trim();
  }

  // Try inline format: **Published:** YYYY-MM-DD HH:MM:SS
  const inlineMatch = markdown.match(/\*\*Published:\*\*\s+(\d{4}-\d{2}-\d{2})/);
  if (inlineMatch) return inlineMatch[1];

  return '';
}

/**
 * Extract author from markdown (inline format)
 * Supports: **Author:** Author Name
 * @param {string} markdown - Markdown content
 * @returns {string} Author name or empty string
 */
function extractAuthor(markdown) {
  const authorMatch = markdown.match(/\*\*Author:\*\*\s+(.+?)$/m);
  return authorMatch ? authorMatch[1].trim() : '';
}

/**
 * Convert slug to human-readable title (fallback)
 * best-hostels-in-varanasi → Best Hostels In Varanasi
 * @param {string} slug - URL slug
 * @returns {string} Title
 */
function slugToTitle(slug) {
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Get metadata for a blog post
 * @param {string} slug - Blog post slug
 * @returns {Promise<{title, excerpt, date, slug}>} Metadata object
 */
async function getBlogMetadata(slug) {
  try {
    const markdown = await loadMarkdownFile(slug);
    return {
      slug,
      title: extractTitle(markdown, slugToTitle(slug)),
      excerpt: extractExcerpt(markdown, 150),
      date: extractDate(markdown) || 'Undated'
    };
  } catch (error) {
    console.error(`Error loading metadata for ${slug}:`, error);
    return {
      slug,
      title: slugToTitle(slug),
      excerpt: 'Error loading blog post',
      date: 'Unknown'
    };
  }
}

/**
 * Get all blog slugs by fetching directory listing
 * Note: Requires server to expose /blogs/ directory listing.
 * Fallback: manually list known slugs if directory listing unavailable.
 * @returns {Promise<string[]>} Array of blog slugs
 */
async function getAllBlogSlugs() {
  // Known blogs (update manually if adding new posts)
  const knownSlugs = [
    'best-hostels-in-varanasi',
    'assi-ghat-varanasi-complete-guide',
    'top-7-experiences-varanasi-traveler',
    'varanasi-solo-female-travelers-safety-travel-guide',
    'things-to-do-varanasi-local-guide',
    'best-time-to-visit-varanasi-month-by-month',
    'varanasi-airport-railway-to-assi-ghat-transfer-guide',
    'varanasi-backpacker-budget-daily-cost-breakdown',
    'is-varanasi-safe-general-guide',
    'sarnath-day-trip-guide-varanasi',
    'assi-ghat-vs-dashashwamedh-where-to-stay',
    'dorm-vs-private-room-varanasi-hostel',
    'varanasi-2-day-itinerary-backpackers',
    'varanasi-3-5-day-itinerary-slow-travel',
    'co-working-spaces-cafes-assi-ghat'
  ];

  return knownSlugs;
}

/**
 * Load and render all blog metadata (for listing page)
 * Static metadata for blog posts (hardcoded to avoid file fetching issues)
 * @returns {Promise<Array>} Array of {title, excerpt, date, slug}
 */
async function getAllBlogsMetadata() {
  const staticMetadata = [
    {
      slug: 'best-hostels-in-varanasi',
      title: 'Best Hostels in Varanasi — 2025 Honest Guide',
      excerpt: 'An honest guide to finding the best hostel in Varanasi — which neighbourhood to choose, what to look for, and why location shapes your entire experience of the city.',
      date: '2026-04-07'
    },
    {
      slug: 'assi-ghat-varanasi-complete-guide',
      title: 'Assi Ghat, Varanasi — Complete Guide for Travelers',
      excerpt: 'The definitive guide to Assi Ghat, Varanasi — geography, atmosphere, boat rides, chai spots, and why it\'s the best base for travelers.',
      date: '2026-07-29'
    },
    {
      slug: 'top-7-experiences-varanasi-traveler',
      title: '7 Experiences Only Varanasi Can Offer — A Traveler\'s Guide',
      excerpt: 'Seven genuine experiences in Varanasi that go beyond the tourist checklist — what to expect and how to make the most of them.',
      date: '2026-05-20'
    },
    {
      slug: 'varanasi-solo-female-travelers-safety-travel-guide',
      title: 'Varanasi for Solo Female Travelers — Safety & Practical Guide',
      excerpt: 'Complete guide for women traveling solo in Varanasi — safety considerations, neighbourhood recommendations, and practical information.',
      date: '2026-05-10'
    },
    {
      slug: 'things-to-do-varanasi-local-guide',
      title: 'Things to Do in Varanasi: Local\'s Guide',
      excerpt: 'Our curated guide to the best things to do in Varanasi — sacred ghats, temples, old-city lanes, and hidden experiences backpackers discover through Mosaic Hostel.',
      date: '2026-07-26'
    },
    {
      slug: 'best-time-to-visit-varanasi-month-by-month',
      title: 'Best Time to Visit Varanasi: Month-by-Month Guide',
      excerpt: 'When is the best time to visit Varanasi? A month-by-month breakdown of weather, festivals, and crowd levels including Dev Deepawali and Holi.',
      date: '2026-07-29'
    },
    {
      slug: 'varanasi-airport-railway-to-assi-ghat-transfer-guide',
      title: 'Varanasi Airport & Railway Station to Assi Ghat: Transfer Guide',
      excerpt: 'How to get from Varanasi\'s airport or railway station to Assi Ghat — routes, timing, and realistic pricing.',
      date: '2026-07-29'
    },
    {
      slug: 'varanasi-backpacker-budget-daily-cost-breakdown',
      title: 'Varanasi Backpacker Budget: Daily Cost Breakdown',
      excerpt: 'How much does a day in Varanasi cost? A realistic daily budget breakdown for backpackers across three budget tiers.',
      date: '2026-07-29'
    },
    {
      slug: 'is-varanasi-safe-general-guide',
      title: 'Is Varanasi Safe? A General Safety Guide for Every Traveler',
      excerpt: 'Is Varanasi safe to visit? An honest general safety guide covering touts, scams, and health precautions.',
      date: '2026-07-29'
    },
    {
      slug: 'sarnath-day-trip-guide-varanasi',
      title: 'Sarnath Day Trip Guide from Varanasi',
      excerpt: 'Everything you need for a Sarnath day trip from Varanasi — how to get there, what to see, and how long to budget.',
      date: '2026-07-29'
    },
    {
      slug: 'assi-ghat-vs-dashashwamedh-where-to-stay',
      title: 'Assi Ghat vs Dashashwamedh: Where Should You Stay in Varanasi?',
      excerpt: 'Assi Ghat or Dashashwamedh - which neighborhood should you actually stay in? A direct, honest comparison for first-time visitors and backpackers.',
      date: '2026-07-29'
    },
    {
      slug: 'dorm-vs-private-room-varanasi-hostel',
      title: 'Dorm vs Private Room in Varanasi: Which Should You Book?',
      excerpt: 'Dorm or private room for your Varanasi stay? A practical breakdown of cost, privacy, and social trade-offs.',
      date: '2026-07-29'
    },
    {
      slug: 'varanasi-2-day-itinerary-backpackers',
      title: '2-Day Varanasi Itinerary for Backpackers',
      excerpt: 'A practical, hour-by-hour 2-day Varanasi itinerary covering the ghats, Sarnath, the old city lanes, and the Ganga Aarti.',
      date: '2026-07-29'
    },
    {
      slug: 'varanasi-3-5-day-itinerary-slow-travel',
      title: '3-5 Day Varanasi Itinerary for Slow Travelers',
      excerpt: 'A 3-5 day Varanasi itinerary for slow travelers and digital nomads who want to actually settle into the city.',
      date: '2026-07-29'
    },
    {
      slug: 'co-working-spaces-cafes-assi-ghat',
      title: 'Co-working Spaces & Cafes Near Assi Ghat for Remote Work',
      excerpt: 'Working remotely from Varanasi? A practical guide to reliable WiFi, cafes suited for laptop work, and how to actually get things done.',
      date: '2026-07-29'
    }
  ];

  // Sort by date (newest first)
  return staticMetadata.sort((a, b) => {
    const dateA = new Date(a.date || 0);
    const dateB = new Date(b.date || 0);
    return dateB - dateA;
  });
}

// Export functions (for use in HTML)
window.blogRenderer = {
  loadMarkdownFile,
  parseMarkdown,
  extractTitle,
  extractExcerpt,
  extractDate,
  extractAuthor,
  slugToTitle,
  getBlogMetadata,
  getAllBlogSlugs,
  getAllBlogsMetadata
};
