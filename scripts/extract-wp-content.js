#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ponytail: simple regex-based SQL parser, good enough for WordPress dumps.
// Upgrade path: use a real SQL parser library if schema changes materially.

// Accept multiple SQL file paths from command-line arguments
// Default: V6VvD.mosaichostels-com (correct Hostinger backup for mosaichostels.com)
const DEFAULT_SQLS = [
  path.join(__dirname, '../untitled folder/u738123768_V6VvD.mosaichostels-com.20260623142824.sql'),
];

const SQL_FILES = process.argv.slice(2).length > 0
  ? process.argv.slice(2).map(arg => {
      const fileName = arg.endsWith('.sql') ? arg : `u738123768_${arg}.20260623142824.sql`;
      return path.join(__dirname, '../untitled folder', fileName);
    })
  : DEFAULT_SQLS;

const OUTPUT_DIR = path.join(__dirname, '../tmp');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Parse SQL value field - handles quoted strings with escapes.
 */
function parseSqlField(fieldStr) {
  fieldStr = fieldStr.trim();
  if (fieldStr === 'NULL') return null;
  if (!fieldStr.startsWith("'")) return fieldStr;

  // Remove surrounding quotes and unescape
  return fieldStr.slice(1, -1)
    .replace(/\\'/g, "'")
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, '\\')
    .replace(/\n/g, '\n'); // Preserve actual newlines
}

/**
 * Extract rows from VALUES section by parsing character-by-character.
 */
function extractRowsFromValues(valuesSection) {
  const rows = [];
  let currentRow = '';
  let depth = 0;
  let inQuote = false;
  let escaped = false;

  for (let i = 0; i < valuesSection.length; i++) {
    const char = valuesSection[i];

    if (escaped) {
      currentRow += char;
      escaped = false;
      continue;
    }

    if (char === '\\' && inQuote) {
      escaped = true;
      currentRow += char;
      continue;
    }

    if (char === "'" && !escaped) {
      inQuote = !inQuote;
      currentRow += char;
      continue;
    }

    if (!inQuote) {
      if (char === '(') {
        depth++;
      } else if (char === ')') {
        depth--;
        currentRow += char;
        if (depth === 0) {
          // End of a row
          const row = currentRow.slice(1, -1).trim(); // Remove outer parens
          if (row) {
            rows.push(row);
          }
          currentRow = '';
          // Skip comma and whitespace after )
          while (i + 1 < valuesSection.length && /[,\s]/.test(valuesSection[i + 1])) {
            i++;
          }
          continue;
        }
      }
    }

    currentRow += char;
  }

  return rows;
}

/**
 * Parse fields from a row string (comma-separated, quoted values).
 */
function parseRowFields(rowStr) {
  const fields = [];
  let current = '';
  let inQuote = false;
  let escaped = false;

  for (let i = 0; i < rowStr.length; i++) {
    const char = rowStr[i];

    if (escaped) {
      current += char;
      escaped = false;
      continue;
    }

    if (char === '\\' && inQuote) {
      escaped = true;
      current += char;
      continue;
    }

    if (char === "'" && !escaped) {
      inQuote = !inQuote;
      current += char;
      continue;
    }

    if (char === ',' && !inQuote) {
      fields.push(parseSqlField(current));
      current = '';
      continue;
    }

    current += char;
  }

  if (current) {
    fields.push(parseSqlField(current));
  }

  return fields;
}

/**
 * Extract WordPress posts (pages and blog posts).
 */
function extractPosts(sqlContent) {
  const pages = [];
  const posts = [];

  // Find the wp_posts VALUES section
  const postsMatch = sqlContent.match(/INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!postsMatch) return { pages, posts };

  const valuesSection = postsMatch[1];
  const rows = extractRowsFromValues(valuesSection);

  rows.forEach(rowStr => {
    if (!rowStr.trim()) return;

    try {
      const fields = parseRowFields(rowStr);
      if (fields.length < 23) return; // wp_posts has 23 columns

      // Map to column names (order from CREATE TABLE wp_posts)
      const post = {
        id: parseInt(fields[0], 10),
        author: parseInt(fields[1], 10),
        date: fields[2],
        date_gmt: fields[3],
        content: fields[4] || '',
        title: fields[5] || '',
        excerpt: fields[6] || '',
        status: fields[7] || '',
        comment_status: fields[8] || '',
        ping_status: fields[9] || '',
        password: fields[10] || '',
        slug: fields[11] || '',
        to_ping: fields[12] || '',
        pinged: fields[13] || '',
        modified: fields[14],
        modified_gmt: fields[15],
        content_filtered: fields[16] || '',
        parent: parseInt(fields[17], 10),
        guid: fields[18] || '',
        menu_order: parseInt(fields[19], 10),
        type: fields[20] || '',
        mime_type: fields[21] || '',
        comment_count: parseInt(fields[22], 10),
      };

      // Only include published pages and posts
      if (post.status !== 'publish') return;
      if (!['page', 'post'].includes(post.type)) return;

      const item = {
        id: post.id,
        slug: post.slug,
        title: post.title,
        content: post.content,
        excerpt: post.excerpt,
        featured_image: '',
        meta_description: '',
        og_title: '',
        og_description: '',
        date: post.date ? post.date.split(' ')[0] : '',
        author: 'Mosaic Hostel Team',
        schema_markup: {},
      };

      if (post.type === 'page') {
        pages.push(item);
      } else {
        posts.push(item);
      }
    } catch (e) {
      // Skip malformed rows silently
    }
  });

  return { pages, posts };
}

/**
 * Extract site metadata from wp_options table.
 */
function extractMeta(sqlContent) {
  const meta = {
    site_title: 'Mosaic Hostel Varanasi — Near Assi Ghat',
    site_description: 'Affordable community hostel in Varanasi',
    site_url: 'https://www.mosaichostels.com',
    phone: '+91-9125492225',
    email: 'mosaichostels@gmail.com',
    address: 'B1/85C, Assi Ghat Road, Near Mumukshu Bhawan, Varanasi, Uttar Pradesh',
    lat: 25.2808,
    lng: 82.9979,
    logo_url: 'https://www.mosaichostels.com/wp-content/uploads/Logo-Transperent.webp',
    og_image: 'https://www.mosaichostels.com/wp-content/uploads/mosaic-hostel-og-image.png',
  };

  // Find the wp_options VALUES section
  const optionsMatch = sqlContent.match(/INSERT INTO `wp_options` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!optionsMatch) return meta;

  const valuesSection = optionsMatch[1];
  const rows = extractRowsFromValues(valuesSection);
  const optionMap = {};

  rows.forEach(rowStr => {
    if (!rowStr.trim()) return;

    try {
      const fields = parseRowFields(rowStr);
      if (fields.length >= 3) {
        // wp_options: (option_id, option_name, option_value, autoload)
        optionMap[fields[1]] = fields[2];
      }
    } catch (e) {
      // Skip malformed options
    }
  });

  // Override with extracted values
  if (optionMap.blogname) meta.site_title = optionMap.blogname;
  if (optionMap.blogdescription) meta.site_description = optionMap.blogdescription;
  if (optionMap.siteurl) meta.site_url = optionMap.siteurl;
  if (optionMap.home) {
    try {
      const url = new URL(optionMap.home);
      if (url.hostname) {
        meta.site_url = optionMap.home;
      }
    } catch (e) {
      // Invalid URL, skip
    }
  }
  if (optionMap.admin_email) meta.email = optionMap.admin_email;

  return meta;
}

/**
 * Extract attachments (media files) from wp_posts table.
 */
function extractAttachments(sqlContent) {
  const attachments = [];

  // Find the wp_posts VALUES section
  const postsMatch = sqlContent.match(/INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!postsMatch) return attachments;

  const valuesSection = postsMatch[1];
  const rows = extractRowsFromValues(valuesSection);

  rows.forEach(rowStr => {
    if (!rowStr.trim()) return;

    try {
      const fields = parseRowFields(rowStr);
      if (fields.length < 23) return; // wp_posts has 23 columns

      const post = {
        id: parseInt(fields[0], 10),
        type: fields[20] || '',
        mime_type: fields[21] || '',
        guid: fields[18] || '',
        title: fields[5] || '',
      };

      // Only include attachments (media files)
      if (post.type !== 'attachment') return;

      attachments.push({
        id: post.id,
        url: post.guid,
        title: post.title,
        mime_type: post.mime_type,
      });
    } catch (e) {
      // Skip malformed rows silently
    }
  });

  return attachments;
}

/**
 * Extract code snippets from wp_posts (wpcode, snippet types).
 */
function extractSnippets(sqlContent) {
  const snippets = [];

  // Find wp_posts VALUES section
  const postsMatch = sqlContent.match(/INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!postsMatch) return snippets;

  const valuesSection = postsMatch[1];
  const rows = extractRowsFromValues(valuesSection);

  rows.forEach(rowStr => {
    if (!rowStr.trim()) return;

    try {
      const fields = parseRowFields(rowStr);
      if (fields.length < 23) return; // wp_posts has 23 columns

      const post = {
        id: parseInt(fields[0], 10),
        author: parseInt(fields[1], 10),
        date: fields[2] || '',
        content: fields[4] || '',
        title: fields[5] || '',
        slug: fields[11] || '',
        status: fields[7] || '',
        type: fields[20] || '',
      };

      // Extract wpcode or snippet post types
      if (!['wpcode'].includes(post.type)) return;
      if (post.status !== 'publish' && post.status !== 'draft') return;

      snippets.push({
        id: post.id,
        title: post.title,
        slug: post.slug,
        code: post.content,
        type: post.type,
        status: post.status,
        date: post.date,
        action_hook: '',
        priority: 10,
        pages_served: [],
      });
    } catch (e) {
      // Skip malformed rows
    }
  });

  return snippets;
}

/**
 * Extract wp_postmeta for snippet configuration.
 */
function extractSnippetMeta(sqlContent, snippetMap) {
  // Find wp_postmeta VALUES section
  const metaMatch = sqlContent.match(/INSERT INTO `wp_postmeta` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!metaMatch) return;

  const valuesSection = metaMatch[1];
  const rows = extractRowsFromValues(valuesSection);

  rows.forEach(rowStr => {
    if (!rowStr.trim()) return;

    try {
      const fields = parseRowFields(rowStr);
      if (fields.length < 4) return;

      const postId = parseInt(fields[1], 10);
      const metaKey = fields[2] || '';
      const metaValue = fields[3] || '';

      // Update snippet with metadata
      if (snippetMap.has(postId)) {
        const snippet = snippetMap.get(postId);

        if (metaKey === '_wpcode_location') {
          snippet.action_hook = metaValue;
        } else if (metaKey === '_wpcode_priority') {
          snippet.priority = parseInt(metaValue, 10) || 10;
        } else if (metaKey === '_wpcode_pages') {
          try {
            const pages = JSON.parse(metaValue);
            snippet.pages_served = Array.isArray(pages) ? pages : [];
          } catch (e) {
            // Keep empty
          }
        }
      }
    } catch (e) {
      // Skip malformed rows
    }
  });
}

/**
 * Main Execution: Extract from multiple SQL backups with merging.
 */
try {
  // Load and extract from all SQL files
  const pageMap = new Map(); // For deduplication by slug
  const postMap = new Map(); // For deduplication by slug
  const attachmentMap = new Map(); // For deduplication by URL
  const snippetMap = new Map(); // For snippets by ID
  let mergedMeta = null;

  console.log(`\nProcessing ${SQL_FILES.length} backup(s)...\n`);

  SQL_FILES.forEach((sqlFile, idx) => {
    if (!fs.existsSync(sqlFile)) {
      console.warn(`  [${idx + 1}] SKIP: ${path.basename(sqlFile)} (not found)`);
      return;
    }

    console.log(`  [${idx + 1}] Reading: ${path.basename(sqlFile)}`);
    const sql = fs.readFileSync(sqlFile, 'utf8');
    const sizemb = (sql.length / 1024 / 1024).toFixed(2);
    console.log(`      Size: ${sizemb} MB`);

    // Extract content from this backup
    const { pages, posts } = extractPosts(sql);
    const attachments = extractAttachments(sql);
    const snippets = extractSnippets(sql);
    const meta = extractMeta(sql);

    // Update merged metadata (keep first as primary)
    if (!mergedMeta) mergedMeta = meta;

    // Merge pages with deduplication by slug (primary = fYZdV)
    pages.forEach(page => {
      const slug = page.slug || `page-${page.id}`;
      if (!pageMap.has(slug)) {
        pageMap.set(slug, page);
        console.log(`      Page: ${page.title} (${slug})`);
      }
    });

    // Merge posts with deduplication by slug
    posts.forEach(post => {
      const slug = post.slug || `post-${post.id}`;
      if (!postMap.has(slug)) {
        postMap.set(slug, post);
        console.log(`      Post: ${post.title} (${slug})`);
      }
    });

    // Collect all attachments with deduplication by URL
    attachments.forEach(att => {
      if (!attachmentMap.has(att.url)) {
        attachmentMap.set(att.url, att);
      }
    });

    // Merge snippets (by ID)
    snippets.forEach(snippet => {
      if (!snippetMap.has(snippet.id)) {
        snippetMap.set(snippet.id, snippet);
        console.log(`      Snippet: ${snippet.title} (ID: ${snippet.id})`);
      }
    });

    // Extract snippet metadata
    extractSnippetMeta(sql, snippetMap);

    console.log(`      Attachments found: ${attachments.length}`);
    console.log(`      Snippets found: ${snippets.length}`);
  });

  const mergedPages = Array.from(pageMap.values());
  const mergedPosts = Array.from(postMap.values());
  const mergedAttachments = Array.from(attachmentMap.values());
  const mergedSnippets = Array.from(snippetMap.values());

  // Create output directory
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Write JSON files
  fs.writeFileSync(path.join(OUTPUT_DIR, 'pages.json'), JSON.stringify(mergedPages, null, 2));
  fs.writeFileSync(path.join(OUTPUT_DIR, 'posts.json'), JSON.stringify(mergedPosts, null, 2));
  fs.writeFileSync(path.join(OUTPUT_DIR, 'attachments.json'), JSON.stringify(mergedAttachments, null, 2));
  fs.writeFileSync(path.join(OUTPUT_DIR, 'snippets.json'), JSON.stringify(mergedSnippets, null, 2));
  fs.writeFileSync(path.join(OUTPUT_DIR, 'meta.json'), JSON.stringify(mergedMeta, null, 2));

  // Summary
  console.log(`\nExtraction Complete:`);
  console.log(`  Pages:        ${mergedPages.length}`);
  console.log(`  Posts:        ${mergedPosts.length}`);
  console.log(`  Attachments:  ${mergedAttachments.length}`);
  console.log(`  Snippets:     ${mergedSnippets.length}`);
  console.log(`  Site Title:   ${mergedMeta.site_title}`);
  console.log(`  Site URL:     ${mergedMeta.site_url}`);
  console.log(`\nOutput files written to: ${OUTPUT_DIR}\n`);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
