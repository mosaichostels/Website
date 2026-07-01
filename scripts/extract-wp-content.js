#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ponytail: simple regex-based SQL parser, good enough for WordPress dumps.
// Upgrade path: use a real SQL parser library if schema changes materially.

// Accept SQL file path from command-line argument, default to fYZdV (58.9MB with published content)
const DEFAULT_SQL = path.join(__dirname, '../untitled folder/u738123768_fYZdV.20260623142824.sql');
const SQL_FILE = process.argv[2] || DEFAULT_SQL;
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
 * Main extraction logic.
 */
function main() {
  try {
    console.log(`Reading SQL backup: ${SQL_FILE}`);
    const sqlContent = fs.readFileSync(SQL_FILE, 'utf-8');

    console.log('Extracting posts and pages...');
    const { pages, posts } = extractPosts(sqlContent);

    console.log('Extracting site metadata...');
    const meta = extractMeta(sqlContent);

    // Write output files
    const pagesPath = path.join(OUTPUT_DIR, 'pages.json');
    const postsPath = path.join(OUTPUT_DIR, 'posts.json');
    const metaPath = path.join(OUTPUT_DIR, 'meta.json');

    fs.writeFileSync(pagesPath, JSON.stringify(pages, null, 2));
    fs.writeFileSync(postsPath, JSON.stringify(posts, null, 2));
    fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));

    console.log(`✓ Extracted ${pages.length} pages → ${pagesPath}`);
    console.log(`✓ Extracted ${posts.length} posts → ${postsPath}`);
    console.log(`✓ Extracted site metadata → ${metaPath}`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
