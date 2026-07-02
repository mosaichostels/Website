#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SQL_FILES = [
  path.join(__dirname, '../untitled folder/u738123768_V6VvD.mosaichostels-com.20260623142824.sql'),
  path.join(__dirname, '../untitled folder/u738123768_fYZdV.20260623142824.sql'),
  path.join(__dirname, '../untitled folder/u738123768_s829o.20260623142824.sql'),
  path.join(__dirname, '../untitled folder/u738123768_wjLnJ.20260623142824.sql'),
];

const OUTPUT_DIR = path.join(__dirname, '../tmp');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
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
        if (row) rows.push(row);
        currentRow = '';
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
      const v = current.trim();
      if (v === 'NULL') {
        fields.push(null);
      } else if (v.startsWith("'") && v.endsWith("'")) {
        fields.push(v.slice(1, -1).replace(/\\'/g, "'").replace(/\\\\/g, '\\').replace(/\\n/g, '\n'));
      } else {
        fields.push(v);
      }
      current = '';
      continue;
    }

    current += char;
  }

  if (current) {
    const v = current.trim();
    if (v === 'NULL') {
      fields.push(null);
    } else if (v.startsWith("'") && v.endsWith("'")) {
      fields.push(v.slice(1, -1).replace(/\\'/g, "'").replace(/\\\\/g, '\\').replace(/\\n/g, '\n'));
    } else {
      fields.push(v);
    }
  }

  return fields;
}

function extractSnippets(sqlContent) {
  const regex = /INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const snippets = [];
  let match;

  while ((match = regex.exec(sqlContent)) !== null) {
    const rows = extractRowsFromValues(match[1]);
    rows.forEach(row => {
      const fields = parseRowFields(row);
      if (fields.length >= 23) {
        const postId = parseInt(fields[0], 10);
        const postType = fields[20];
        const postStatus = fields[7];
        const postTitle = fields[5];
        const postContent = fields[4] || '';

        if (postType === 'wpcode') {
          snippets.push({
            id: postId,
            title: postTitle,
            status: postStatus,
            content: postContent,
            content_length: postContent.length,
          });
        }
      }
    });
  }

  return snippets;
}

function extractPostmeta(sqlContent, snippetIds) {
  const regex = /INSERT INTO `wp_postmeta` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const postMetaMap = {};
  let match;

  while ((match = regex.exec(sqlContent)) !== null) {
    const rows = extractRowsFromValues(match[1]);
    rows.forEach(row => {
      const fields = parseRowFields(row);
      if (fields.length >= 4) {
        const postId = parseInt(fields[1], 10);
        const metaKey = fields[2] || '';
        const metaValue = fields[3] || '';

        if (snippetIds.includes(postId)) {
          if (!postMetaMap[postId]) {
            postMetaMap[postId] = {};
          }
          postMetaMap[postId][metaKey] = metaValue;
        }
      }
    });
  }

  return postMetaMap;
}

// Main
try {
  console.log('Extracting Code Snippets from all backups...\n');

  const allSnippets = {};

  SQL_FILES.forEach(sqlFile => {
    if (!fs.existsSync(sqlFile)) {
      console.log(`⊗ ${path.basename(sqlFile)} not found`);
      return;
    }

    console.log(`✓ ${path.basename(sqlFile)}`);
    const sql = fs.readFileSync(sqlFile, 'utf8');

    // Extract all snippets
    const snippets = extractSnippets(sql);
    const snippetIds = snippets.map(s => s.id);
    const postMeta = extractPostmeta(sql, snippetIds);

    // Enrich snippets with metadata
    snippets.forEach(snippet => {
      const meta = postMeta[snippet.id] || {};
      snippet.meta = meta;
      snippet.action_hook = meta._wpcode_location || '';
      snippet.priority = meta._wpcode_priority || '10';
      snippet.pages_served = meta._wpcode_pages_served ? JSON.parse(meta._wpcode_pages_served) : [];
    });

    // Group by backup
    allSnippets[path.basename(sqlFile)] = snippets;

    console.log(`  Found ${snippets.length} snippets`);
    snippets.forEach(s => {
      const preview = s.content.substring(0, 50).replace(/\n/g, ' ');
      const truncated = s.content.length > 50 ? '...' : '';
      console.log(`    - ${s.id}: "${s.title}" (${s.status}) [${s.content_length} bytes] ${preview}${truncated}`);
    });
  });

  // Write combined output
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'snippets-all.json'),
    JSON.stringify(allSnippets, null, 2)
  );

  // Write summary
  const summary = {};
  Object.entries(allSnippets).forEach(([backup, snippets]) => {
    summary[backup] = {
      total: snippets.length,
      published: snippets.filter(s => s.status === 'publish').length,
      draft: snippets.filter(s => s.status === 'draft').length,
      snippets: snippets.map(s => ({ id: s.id, title: s.title, status: s.status, size: s.content_length }))
    };
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'snippets-summary.json'),
    JSON.stringify(summary, null, 2)
  );

  console.log(`\nOutput saved:`);
  console.log(`  - ${path.join(OUTPUT_DIR, 'snippets-all.json')}`);
  console.log(`  - ${path.join(OUTPUT_DIR, 'snippets-summary.json')}`);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
