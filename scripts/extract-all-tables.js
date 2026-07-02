#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const SQL_FILE = path.join(__dirname, '../untitled folder/u738123768_V6VvD.mosaichostels-com.20260623142824.sql');
const OUTPUT_DIR = path.join(__dirname, '../tmp');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function extractAllTables(sqlContent) {
  // Find all INSERT INTO statements and their table names
  const regex = /INSERT INTO `([^`]+)` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  const tables = {};
  let match;

  while ((match = regex.exec(sqlContent)) !== null) {
    const tableName = match[1];
    const valuesSection = match[2];

    if (!tables[tableName]) {
      tables[tableName] = {
        name: tableName,
        rowCount: 0,
        size: 0,
        data: []
      };
    }

    // Count rows (approximate - by counting parentheses at row start)
    const rows = valuesSection.split(/\n\(/);
    tables[tableName].rowCount += rows.length - 1;
    tables[tableName].size += valuesSection.length;
  }

  return tables;
}

// Main
try {
  console.log('Reading SQL backup...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  const tables = extractAllTables(sql);

  console.log(`Found ${Object.keys(tables).length} tables\n`);
  console.log('Table Inventory:');
  console.log('================================================\n');

  const sorted = Object.values(tables).sort((a, b) => b.size - a.size);

  let totalRows = 0;
  let totalSize = 0;

  sorted.forEach((table, idx) => {
    console.log(`${idx + 1}. ${table.name}`);
    console.log(`   Rows: ${table.rowCount}, Size: ${(table.size / 1024).toFixed(2)} KB`);
    totalRows += table.rowCount;
    totalSize += table.size;
  });

  console.log(`\n================================================`);
  console.log(`TOTAL: ${Object.keys(tables).length} tables`);
  console.log(`TOTAL ROWS: ${totalRows}`);
  console.log(`TOTAL SIZE: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);

  // Highlight plugin-specific tables that might store Code Snippets
  console.log(`\n\nPlugin-Specific Tables (potential snippet storage):`);
  console.log('================================================\n');

  const pluginTables = sorted.filter(t =>
    t.name.includes('wpcode') ||
    t.name.includes('snippet') ||
    t.name.includes('postmeta') ||
    t.name.includes('options') ||
    t.name.includes('posts')
  );

  if (pluginTables.length > 0) {
    pluginTables.forEach(t => {
      console.log(`✓ ${t.name} (${t.rowCount} rows, ${(t.size / 1024).toFixed(2)} KB)`);
    });
  }

  // Write inventory to JSON
  const inventory = sorted.map(t => ({
    name: t.name,
    rowCount: t.rowCount,
    sizeBytes: t.size,
    sizeKB: (t.size / 1024).toFixed(2)
  }));

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'database-tables-inventory.json'),
    JSON.stringify({ totalTables: sorted.length, tables: inventory }, null, 2)
  );

  console.log(`\nInventory saved: ${path.join(OUTPUT_DIR, 'database-tables-inventory.json')}`);

  // Check specifically for wpcode-related data
  console.log(`\n\nSearching for Code Snippets data...`);
  console.log('================================================\n');

  // Search for wpcode in SQL
  const wpcodeMentions = (sql.match(/wpcode/gi) || []).length;
  const snippetMentions = (sql.match(/snippet/gi) || []).length;
  const metaKeyMentions = (sql.match(/_wpcode/gi) || []).length;

  console.log(`"wpcode" mentions in SQL: ${wpcodeMentions}`);
  console.log(`"snippet" mentions in SQL: ${snippetMentions}`);
  console.log(`"_wpcode" meta keys in SQL: ${metaKeyMentions}`);

  // Check wp_options for code snippets settings
  const optionsMatch = sql.match(/INSERT INTO `wp_options` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/);
  if (optionsMatch) {
    const optionsData = optionsMatch[1];
    const wpcodeinOptions = (optionsData.match(/wpcode/gi) || []).length;
    console.log(`\nwp_options table: "wpcode" settings found: ${wpcodeinOptions}`);

    // Extract option names
    const optionNames = optionsData.match(/\('([^']*)',('[^']*'|[^,]*)/g) || [];
    const snippetRelated = optionNames.filter(opt =>
      opt.includes('code') ||
      opt.includes('snippet') ||
      opt.includes('wpcode')
    );

    if (snippetRelated.length > 0) {
      console.log(`\nCode-related options found:`);
      snippetRelated.slice(0, 20).forEach(opt => {
        console.log(`  - ${opt.substring(0, 80)}`);
      });
    }
  }

} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
