#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SQL_FILE = path.join(__dirname, '../untitled folder/u738123768_V6VvD.mosaichostels-com.20260623142824.sql');
const OUTPUT_DIR = path.join(__dirname, '../tmp');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function parseSqlField(fieldStr) {
  fieldStr = fieldStr.trim();
  if (fieldStr === 'NULL') return null;
  if (!fieldStr.startsWith("'")) return fieldStr;

  return fieldStr.slice(1, -1)
    .replace(/\\'/g, "'")
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, '\\')
    .replace(/\\n/g, '\n');
}

function extractRowsFromValues(valuesSection) {
  const rows = [];
  let currentRow = '';
  let inQuote = false;

  for (let i = 0; i < valuesSection.length; i++) {
    const char = valuesSection[i];

    if (char === "'" && (i === 0 || valuesSection[i - 1] !== '\\')) {
      inQuote = !inQuote;
    }

    if (char === ')' && !inQuote) {
      currentRow += char;
      if (currentRow.trim().endsWith(')')) {
        const row = currentRow.slice(1, -1).trim();
        if (row) {
          rows.push(row);
        }
        currentRow = '';
        while (i + 1 < valuesSection.length && /[,\s]/.test(valuesSection[i + 1])) {
          i++;
        }
        continue;
      }
    }

    currentRow += char;
  }

  return rows;
}

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

function extractPages(sqlContent) {
  const regex = /INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const pages = [];
  let match;

  while ((match = regex.exec(sqlContent)) !== null) {
    const valuesSection = match[1];
    const rows = extractRowsFromValues(valuesSection);

    rows.forEach(rowStr => {
      if (!rowStr.trim()) return;
      try {
        const fields = parseRowFields(rowStr);
        if (fields.length < 23) return;

        const postId = parseInt(fields[0], 10);
        const postType = fields[20] || '';
        const postStatus = fields[7] || '';
        const postTitle = fields[5] || '';
        const postSlug = fields[11] || '';
        const postContent = fields[4] || '';

        // Only published pages
        if (postStatus !== 'publish' || postType !== 'page') return;

        pages.push({
          id: postId,
          title: postTitle,
          slug: postSlug,
          content: postContent,
          type: postType,
        });
      } catch (e) {
        // Skip malformed rows
      }
    });
  }

  return pages;
}

function extractPostmeta(sqlContent, pageIds) {
  const regex = /INSERT INTO `wp_postmeta` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const postMetaMap = {};
  let match;

  while ((match = regex.exec(sqlContent)) !== null) {
    const valuesSection = match[1];
    const rows = extractRowsFromValues(valuesSection);

    rows.forEach(rowStr => {
      if (!rowStr.trim()) return;
      try {
        const fields = parseRowFields(rowStr);
        if (fields.length < 4) return;

        const postId = parseInt(fields[1], 10);
        const metaKey = fields[2] || '';
        const metaValue = fields[3] || '';

        // Only for our pages
        if (!pageIds.includes(postId)) return;

        if (!postMetaMap[postId]) {
          postMetaMap[postId] = {};
        }

        postMetaMap[postId][metaKey] = metaValue;
      } catch (e) {
        // Skip malformed rows
      }
    });
  }

  return postMetaMap;
}

function elementorToText(elementorJson) {
  try {
    const data = JSON.parse(elementorJson);
    let text = '';

    function traverse(element) {
      if (!element) return;

      if (element.settings) {
        const settings = element.settings;

        // Extract text content
        if (settings.editor_content) {
          text += settings.editor_content + '\n';
        }
        if (settings.title) {
          text += settings.title + '\n';
        }
        if (settings.description) {
          text += settings.description + '\n';
        }
        if (settings.button_text) {
          text += settings.button_text + '\n';
        }
        if (settings.text) {
          text += settings.text + '\n';
        }
      }

      if (element.elements && Array.isArray(element.elements)) {
        element.elements.forEach(child => traverse(child));
      }
    }

    if (Array.isArray(data)) {
      data.forEach(elem => traverse(elem));
    } else {
      traverse(data);
    }

    return text.trim();
  } catch (e) {
    return '';
  }
}

// Main
try {
  if (!fs.existsSync(SQL_FILE)) {
    console.error(`SQL file not found: ${SQL_FILE}`);
    process.exit(1);
  }

  console.log(`Reading SQL backup...\n`);
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  // Extract pages
  const pages = extractPages(sql);
  console.log(`Found ${pages.length} published pages`);
  pages.forEach(p => console.log(`  - ${p.title} (ID: ${p.id}, slug: ${p.slug})`));

  if (pages.length === 0) {
    console.log('No pages found');
    process.exit(0);
  }

  // Extract postmeta
  const pageIds = pages.map(p => p.id);
  const postMeta = extractPostmeta(sql, pageIds);

  console.log(`\nExtracting Elementor data...\n`);

  // Enrich pages with Elementor content
  pages.forEach(page => {
    const meta = postMeta[page.id] || {};
    const elementorData = meta._elementor_data || '';

    if (elementorData) {
      page.elementor_data = elementorData;
      const textContent = elementorToText(elementorData);
      page.text_preview = textContent.substring(0, 500); // First 500 chars
      console.log(`✓ ${page.title} (${elementorData.length} bytes of Elementor data)`);
    } else {
      console.log(`✗ ${page.title} (no Elementor data found)`);
    }
  });

  // Write output
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'elementor-pages-raw.json'),
    JSON.stringify(pages, null, 2)
  );

  console.log(`\nOutput saved to: ${path.join(OUTPUT_DIR, 'elementor-pages-raw.json')}`);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
