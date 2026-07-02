#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SQL_FILE = path.join(__dirname, '../untitled folder/u738123768_V6VvD.mosaichostels-com.20260623142824.sql');
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

// Main
try {
  console.log('Extracting full content from wp_posts...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  // Get ALL wp_posts sections
  const regex = /INSERT INTO `wp_posts` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const allContent = [];
  let match;
  let sectionNum = 0;

  while ((match = regex.exec(sql)) !== null) {
    sectionNum++;
    console.log(`Processing wp_posts section ${sectionNum}...`);
    const rows = extractRowsFromValues(match[1]);

    rows.forEach(row => {
      const fields = parseRowFields(row);
      if (fields.length >= 23) {
        const postId = parseInt(fields[0], 10);
        const postTitle = fields[5];
        const postType = fields[20];
        const postStatus = fields[7];
        const postContent = fields[4] || '';

        // Save if content is substantial
        if (postContent && postContent.length > 100) {
          allContent.push({
            id: postId,
            title: postTitle,
            type: postType,
            status: postStatus,
            content: postContent,
            contentLength: postContent.length
          });
        }
      }
    });
  }

  console.log(`Found ${allContent.length} entries with substantial content\n`);

  // Sort by content length descending
  allContent.sort((a, b) => b.contentLength - a.contentLength);

  // Write individual files
  const contentDir = path.join(OUTPUT_DIR, 'extracted-content');
  if (!fs.existsSync(contentDir)) {
    fs.mkdirSync(contentDir, { recursive: true });
  }

  allContent.forEach((item, idx) => {
    const filename = `${item.id}-${item.type}-${item.title.replace(/[^\w]/g, '_').substring(0, 30)}.html`;
    const filepath = path.join(contentDir, filename);

    const wrapper = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${item.title}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    .meta { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .meta p { margin: 5px 0; }
    .content { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
  </style>
</head>
<body>
  <h1>${item.title}</h1>
  <div class="meta">
    <p><strong>ID:</strong> ${item.id}</p>
    <p><strong>Type:</strong> ${item.type}</p>
    <p><strong>Status:</strong> ${item.status}</p>
    <p><strong>Size:</strong> ${item.contentLength} bytes</p>
  </div>
  <div class="content">
    ${item.content}
  </div>
</body>
</html>`;

    fs.writeFileSync(filepath, wrapper);
    console.log(`✓ ${item.id}: "${item.title}" (${item.type}, ${item.contentLength} bytes)`);
  });

  // Write JSON summary
  const summary = allContent.map(c => ({
    id: c.id,
    title: c.title,
    type: c.type,
    status: c.status,
    contentLength: c.contentLength
  }));

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'extracted-content-summary.json'),
    JSON.stringify(summary, null, 2)
  );

  console.log(`\nFiles saved to: ${contentDir}`);
  console.log(`Summary: ${path.join(OUTPUT_DIR, 'extracted-content-summary.json')}`);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
