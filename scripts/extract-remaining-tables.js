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

// Extract table data
function extractTable(sql, tableName) {
  const regex = new RegExp(`INSERT INTO \\\`${tableName}\\\` VALUES\\n([\\s\\S]*?)(?=\\);?\\s*(?:\\/\\*|INSERT|SET|$))`, 'i');
  const match = sql.match(regex);

  if (!match) return null;

  const rows = extractRowsFromValues(match[1]);
  const data = [];

  rows.forEach(row => {
    try {
      const fields = parseRowFields(row);
      data.push(fields);
    } catch (e) {
      // Skip malformed
    }
  });

  return data;
}

// Main
try {
  console.log('Extracting remaining important tables...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  // 1. Extract wp_terms
  console.log('1. wp_terms table...');
  const terms = extractTable(sql, 'wp_terms');
  if (terms) {
    console.log(`   Found ${terms.length} terms`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-terms.json'),
      JSON.stringify({
        count: terms.length,
        data: terms.map(t => ({ id: t[0], name: t[1], slug: t[2], group: t[3] }))
      }, null, 2)
    );
  }

  // 2. Extract wp_term_taxonomy
  console.log('2. wp_term_taxonomy table...');
  const termTax = extractTable(sql, 'wp_term_taxonomy');
  if (termTax) {
    console.log(`   Found ${termTax.length} term taxonomies`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-term-taxonomy.json'),
      JSON.stringify({
        count: termTax.length,
        data: termTax.map(t => ({ termId: t[0], taxonomy: t[1], description: t[2], parent: t[3], count: t[4] }))
      }, null, 2)
    );
  }

  // 3. Extract wp_term_relationships
  console.log('3. wp_term_relationships table...');
  const termRel = extractTable(sql, 'wp_term_relationships');
  if (termRel) {
    console.log(`   Found ${termRel.length} term relationships`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-term-relationships.json'),
      JSON.stringify({
        count: termRel.length,
        data: termRel.map(t => ({ objectId: t[0], termTaxonomyId: t[1], termOrder: t[2] }))
      }, null, 2)
    );
  }

  // 4. Extract wp_users
  console.log('4. wp_users table...');
  const users = extractTable(sql, 'wp_users');
  if (users && users.length > 0) {
    console.log(`   Found ${users.length} users`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-users.json'),
      JSON.stringify({
        count: users.length,
        data: users.map(u => ({
          id: u[0],
          login: u[1],
          email: u[3],
          registered: u[5],
          displayName: u[7]
        }))
      }, null, 2)
    );
  } else {
    console.log('   No users found');
  }

  // 5. Extract wp_usermeta
  console.log('5. wp_usermeta table...');
  const userMeta = extractTable(sql, 'wp_usermeta');
  if (userMeta) {
    console.log(`   Found ${userMeta.length} user metadata entries`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-usermeta.json'),
      JSON.stringify({
        count: userMeta.length,
        data: userMeta.map(m => ({ userId: m[0], metaKey: m[1], metaValue: m[2] }))
      }, null, 2)
    );
  }

  // 6. Extract wp_rank_math_* tables
  console.log('6. Rank Math SEO tables...');
  const rankMathTables = [
    'wp_rank_math_analytics_objects',
    'wp_rank_math_analytics_gsc',
    'wp_rank_math_analytics_inspections',
    'wp_rank_math_404_logs',
    'wp_rank_math_internal_links',
    'wp_rank_math_internal_meta',
    'wp_rank_math_redirections'
  ];

  const rankMathData = {};
  rankMathTables.forEach(table => {
    const data = extractTable(sql, table);
    if (data) {
      rankMathData[table] = { count: data.length, data };
      console.log(`   ${table}: ${data.length} rows`);
    }
  });

  if (Object.keys(rankMathData).length > 0) {
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-rank-math-tables.json'),
      JSON.stringify(rankMathData, null, 2)
    );
  }

  // 7. Extract wp_yoast_* tables
  console.log('7. Yoast SEO tables...');
  const yoastTables = [
    'wp_yoast_indexable',
    'wp_yoast_indexable_hierarchy',
    'wp_yoast_migrations',
    'wp_yoast_seo_links'
  ];

  const yoastData = {};
  yoastTables.forEach(table => {
    const data = extractTable(sql, table);
    if (data) {
      yoastData[table] = { count: data.length, data };
      console.log(`   ${table}: ${data.length} rows`);
    }
  });

  if (Object.keys(yoastData).length > 0) {
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-yoast-tables.json'),
      JSON.stringify(yoastData, null, 2)
    );
  }

  // 8. Extract wp_forminator_form_entry
  console.log('8. Forminator form entries...');
  const formEntries = extractTable(sql, 'wp_frmt_form_entry');
  if (formEntries) {
    console.log(`   Found ${formEntries.length} form entries`);
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'wp-forminator-entries.json'),
      JSON.stringify({
        count: formEntries.length,
        data: formEntries
      }, null, 2)
    );
  }

  console.log('\n✅ All remaining tables extracted\n');
  console.log('Files saved:');
  console.log('  ✓ wp-terms.json');
  console.log('  ✓ wp-term-taxonomy.json');
  console.log('  ✓ wp-term-relationships.json');
  console.log('  ✓ wp-users.json');
  console.log('  ✓ wp-usermeta.json');
  console.log('  ✓ wp-rank-math-tables.json');
  console.log('  ✓ wp-yoast-tables.json');
  console.log('  ✓ wp-forminator-entries.json');

} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
