// ── MARKDOWN RENDERING UTILITIES ──
// Client-side markdown to HTML conversion for blog system

/**
 * Fetch a markdown file by slug
 * @param {string} slug - Blog post slug (filename without .md)
 * @returns {Promise<string>} Markdown content
 */
async function loadMarkdownFile(slug) {
  const response = await fetch(`/blogs/${slug}.md`);
  if (!response.ok) {
    throw new Error(`Failed to load blog post: ${slug}`);
  }
  return await response.text();
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
  return marked.parse(markdown);
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
 * Extract date from markdown frontmatter
 * Expects YAML frontmatter: ---\ndate: YYYY-MM-DD\n---
 * @param {string} markdown - Markdown content
 * @returns {string} Date (YYYY-MM-DD format) or empty string
 */
function extractDate(markdown) {
  const frontmatterMatch = markdown.match(/^---\n([\s\S]+?)\n---/);
  if (!frontmatterMatch) return '';

  const dateMatch = frontmatterMatch[1].match(/date:\s*(.+?)$/m);
  return dateMatch ? dateMatch[1].trim() : '';
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
    'why-assi-ghat-perfect-base-varanasi-stay'
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
      excerpt: 'The definitive guide to Assi Ghat, Varanasi — geography, atmosphere, practical information, and why it\'s the best base for travelers.',
      date: '2026-06-15'
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
      slug: 'why-assi-ghat-perfect-base-varanasi-stay',
      title: 'Why Assi Ghat is the Perfect Base for Your Varanasi Stay',
      excerpt: 'Why experienced travelers choose Assi Ghat over other neighbourhoods in Varanasi — location benefits, atmosphere, and local access.',
      date: '2026-03-15'
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
  slugToTitle,
  getBlogMetadata,
  getAllBlogSlugs,
  getAllBlogsMetadata
};
