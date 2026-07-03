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
    'hostel-near-assi-ghat-varanasi',
    'backpackers-guide-assi-ghat-varanasi',
    'varanasi-solo-female-travelers-safety-travel-guide',
    'top-7-experiences-varanasi-traveler',
    'why-assi-ghat-perfect-base-varanasi-stay'
  ];

  return knownSlugs;
}

/**
 * Load and render all blog metadata (for listing page)
 * @returns {Promise<Array>} Array of {title, excerpt, date, slug}
 */
async function getAllBlogsMetadata() {
  const slugs = await getAllBlogSlugs();
  const metadataArray = await Promise.all(
    slugs.map(slug => getBlogMetadata(slug))
  );

  // Sort by date (newest first)
  return metadataArray.sort((a, b) => {
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
