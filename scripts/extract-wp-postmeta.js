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
  console.log('Extracting wp_postmeta table...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  // Extract all wp_postmeta sections
  const regex = /INSERT INTO `wp_postmeta` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  let match;
  let totalRows = 0;
  const allMetadata = {};
  const metaKeyStats = {};

  while ((match = regex.exec(sql)) !== null) {
    const rows = extractRowsFromValues(match[1]);
    console.log(`Processing wp_postmeta section with ${rows.length} rows`);

    rows.forEach((row, idx) => {
      try {
        const fields = parseRowFields(row);
        // wp_postmeta: meta_id, post_id, meta_key, meta_value
        if (fields.length >= 4) {
          const metaId = fields[0];
          const postId = parseInt(fields[1], 10);
          const metaKey = fields[2];
          const metaValue = fields[3];

          totalRows++;

          // Track meta keys
          if (!metaKeyStats[metaKey]) {
            metaKeyStats[metaKey] = { count: 0, size: 0 };
          }
          metaKeyStats[metaKey].count++;
          metaKeyStats[metaKey].size += metaValue ? metaValue.length : 0;

          // Group by post_id
          if (!allMetadata[postId]) {
            allMetadata[postId] = [];
          }
          allMetadata[postId].push({
            metaId,
            metaKey,
            metaValue,
            valueLength: metaValue ? metaValue.length : 0
          });
        }
      } catch (e) {
        // Skip malformed rows
      }
    });
  }

  console.log(`\nTotal metadata entries: ${totalRows}`);
  console.log(`Total posts with metadata: ${Object.keys(allMetadata).length}\n`);

  // Sort meta keys by frequency
  const sortedKeys = Object.entries(metaKeyStats)
    .sort((a, b) => b[1].count - a[1].count);

  console.log('Top 30 Meta Keys by Frequency:');
  console.log('================================================\n');
  sortedKeys.slice(0, 30).forEach(([key, stats], idx) => {
    console.log(`${idx + 1}. ${key}`);
    console.log(`   Count: ${stats.count}, Total Size: ${(stats.size / 1024).toFixed(2)} KB`);
  });

  // Write full metadata by post_id
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-by-post.json'),
    JSON.stringify({
      timestamp: new Date().toISOString(),
      totalEntries: totalRows,
      totalPosts: Object.keys(allMetadata).length,
      data: allMetadata
    }, null, 2)
  );

  // Write meta key statistics
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-keys-stats.json'),
    JSON.stringify({
      totalUniqueKeys: sortedKeys.length,
      stats: Object.fromEntries(sortedKeys)
    }, null, 2)
  );

  // Extract specific important metadata
  const importantKeys = [
    '_elementor_data',
    '_elementor_version',
    '_wp_page_template',
    '_yoast_wpseo_title',
    '_yoast_wpseo_metadesc',
    '_yoast_wpseo_canonical',
    '_thumbnail_id',
    '_edit_lock',
    '_edit_last',
    '_wp_old_slug'
  ];

  const importantMeta = {};
  Object.entries(allMetadata).forEach(([postId, metas]) => {
    const important = metas.filter(m => importantKeys.includes(m.metaKey));
    if (important.length > 0) {
      importantMeta[postId] = important;
    }
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-important.json'),
    JSON.stringify({
      importantKeys,
      matchingEntries: Object.keys(importantMeta).length,
      data: importantMeta
    }, null, 2)
  );

  // Extract Elementor data specifically
  const elementorMeta = {};
  Object.entries(allMetadata).forEach(([postId, metas]) => {
    const elem = metas.filter(m => m.metaKey.includes('elementor'));
    if (elem.length > 0) {
      elementorMeta[postId] = elem;
    }
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-elementor.json'),
    JSON.stringify({
      postsWithElementor: Object.keys(elementorMeta).length,
      data: elementorMeta
    }, null, 2)
  );

  // Extract SEO metadata
  const seoMeta = {};
  Object.entries(allMetadata).forEach(([postId, metas]) => {
    const seo = metas.filter(m =>
      m.metaKey.includes('yoast') ||
      m.metaKey.includes('rank_math') ||
      m.metaKey.includes('seo')
    );
    if (seo.length > 0) {
      seoMeta[postId] = seo;
    }
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-seo.json'),
    JSON.stringify({
      postsWithSEO: Object.keys(seoMeta).length,
      data: seoMeta
    }, null, 2)
  );

  // Extract image/media metadata
  const mediaMeta = {};
  Object.entries(allMetadata).forEach(([postId, metas]) => {
    const media = metas.filter(m =>
      m.metaKey.includes('image') ||
      m.metaKey.includes('thumbnail') ||
      m.metaKey.includes('attachment') ||
      m.metaKey.includes('media')
    );
    if (media.length > 0) {
      mediaMeta[postId] = media;
    }
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-postmeta-media.json'),
    JSON.stringify({
      postsWithMediaMeta: Object.keys(mediaMeta).length,
      data: mediaMeta
    }, null, 2)
  );

  console.log(`\n\nFiles saved:`);
  console.log(`  ✓ wp-postmeta-by-post.json (${totalRows} entries)`);
  console.log(`  ✓ wp-postmeta-keys-stats.json (${sortedKeys.length} unique keys)`);
  console.log(`  ✓ wp-postmeta-important.json (${Object.keys(importantMeta).length} posts)`);
  console.log(`  ✓ wp-postmeta-elementor.json (${Object.keys(elementorMeta).length} posts)`);
  console.log(`  ✓ wp-postmeta-seo.json (${Object.keys(seoMeta).length} posts)`);
  console.log(`  ✓ wp-postmeta-media.json (${Object.keys(mediaMeta).length} posts)`);

} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
