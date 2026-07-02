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
  console.log('Extracting wp_snippets table...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  const match = sql.match(/INSERT INTO `wp_snippets` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (!match) {
    console.log('wp_snippets table not found');
    process.exit(1);
  }

  const rows = extractRowsFromValues(match[1]);
  console.log(`Found ${rows.length} snippets in wp_snippets table\n`);

  const snippets = [];

  rows.forEach((row, idx) => {
    try {
      const fields = parseRowFields(row);
      // wp_snippets columns: id, name, desc, code, scope, priority, active, created, modified
      // Adjust based on actual table structure

      const snippet = {
        id: fields[0],
        name: fields[1] || '',
        description: fields[2] || '',
        code: fields[3] || '',
        scope: fields[4] || 'global', // global, theme, plugin
        priority: parseInt(fields[5]) || 10,
        active: fields[6] || 1,
        created: fields[7] || '',
        modified: fields[8] || '',
        codeLength: fields[3] ? fields[3].length : 0
      };

      snippets.push(snippet);

      console.log(`${idx + 1}. ${snippet.name || '(untitled)'}`);
      console.log(`   ID: ${snippet.id}, Active: ${snippet.active}, Size: ${snippet.codeLength} bytes`);
      if (snippet.description) {
        console.log(`   Description: ${snippet.description}`);
      }
      console.log();
    } catch (e) {
      console.log(`Error parsing row ${idx + 1}: ${e.message}`);
    }
  });

  // Write to JSON
  const jsonOutput = {
    timestamp: new Date().toISOString(),
    totalSnippets: snippets.length,
    source: 'wp_snippets table (mosaichostels.com backup)',
    snippets: snippets
  };

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-snippets-full-extract.json'),
    JSON.stringify(jsonOutput, null, 2)
  );

  // Write individual files for each snippet
  const snippetDir = path.join(OUTPUT_DIR, 'snippets');
  if (!fs.existsSync(snippetDir)) {
    fs.mkdirSync(snippetDir);
  }

  snippets.forEach(snippet => {
    const filename = `${snippet.id}-${(snippet.name || 'untitled').replace(/[^\w]/g, '_').substring(0, 40)}.php`;
    const filepath = path.join(snippetDir, filename);

    const header = `/**
 * Snippet ID: ${snippet.id}
 * Name: ${snippet.name}
 * Scope: ${snippet.scope}
 * Priority: ${snippet.priority}
 * Active: ${snippet.active}
 * Created: ${snippet.created}
 * Modified: ${snippet.modified}
 * Size: ${snippet.codeLength} bytes
 */\n\n`;

    const content = header + (snippet.code || '');
    fs.writeFileSync(filepath, content);
  });

  // Write summary
  const summary = snippets.map(s => ({
    id: s.id,
    name: s.name,
    scope: s.scope,
    active: s.active,
    codeLength: s.codeLength,
    isPageTemplate: s.code && s.code.includes('template_redirect') ? 'YES' : 'NO'
  }));

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-snippets-summary.json'),
    JSON.stringify({
      totalSnippets: snippets.length,
      summary: summary
    }, null, 2)
  );

  console.log(`\nFiles saved:`);
  console.log(`  - ${path.join(OUTPUT_DIR, 'wp-snippets-full-extract.json')}`);
  console.log(`  - ${path.join(OUTPUT_DIR, 'wp-snippets-summary.json')}`);
  console.log(`  - ${snippetDir}/ (${snippets.length} individual .php files)`);

} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
