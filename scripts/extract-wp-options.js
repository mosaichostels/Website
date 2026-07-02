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
  console.log('Extracting wp_options table...\n');
  const sql = fs.readFileSync(SQL_FILE, 'utf8');

  // Extract all wp_options sections
  const regex = /INSERT INTO `wp_options` VALUES\n([\s\S]*?)(?=\);?\s*(?:\/\*|INSERT|SET|$))/g;
  let match;
  let totalRows = 0;
  const allOptions = {};
  const optionGroups = {
    wordpress: {},
    plugins: {},
    theme: {},
    seo: {},
    cache: {},
    forms: {},
    other: {}
  };

  while ((match = regex.exec(sql)) !== null) {
    const rows = extractRowsFromValues(match[1]);
    console.log(`Processing wp_options section with ${rows.length} rows`);

    rows.forEach((row, idx) => {
      try {
        const fields = parseRowFields(row);
        // wp_options: option_id, option_name, option_value, autoload
        if (fields.length >= 3) {
          const optionId = fields[0];
          const optionName = fields[1];
          const optionValue = fields[2];
          const autoload = fields[3];

          totalRows++;

          const option = {
            optionId,
            optionName,
            optionValue,
            autoload,
            valueLength: optionValue ? optionValue.length : 0,
            isSerialized: optionValue && (optionValue.startsWith('a:') || optionValue.startsWith('O:')),
            isJson: optionValue && (optionValue.startsWith('{') || optionValue.startsWith('['))
          };

          allOptions[optionName] = option;

          // Categorize
          if (optionName.startsWith('siteurl') || optionName.startsWith('home') ||
              optionName.startsWith('blogname') || optionName.startsWith('admin_email')) {
            optionGroups.wordpress[optionName] = option;
          } else if (optionName.includes('elementor') || optionName.includes('yoast') ||
                     optionName.includes('rank_math') || optionName.includes('wpcode') ||
                     optionName.includes('forminator') || optionName.includes('litespeed')) {
            optionGroups.plugins[optionName] = option;
          } else if (optionName.startsWith('theme_') || optionName.includes('astra') ||
                     optionName.includes('template')) {
            optionGroups.theme[optionName] = option;
          } else if (optionName.includes('yoast') || optionName.includes('seo') ||
                     optionName.includes('rank_math')) {
            optionGroups.seo[optionName] = option;
          } else if (optionName.includes('cache') || optionName.includes('litespeed')) {
            optionGroups.cache[optionName] = option;
          } else if (optionName.includes('form') || optionName.includes('forminator')) {
            optionGroups.forms[optionName] = option;
          } else {
            optionGroups.other[optionName] = option;
          }
        }
      } catch (e) {
        // Skip malformed rows
      }
    });
  }

  console.log(`\nTotal options: ${totalRows}`);
  console.log(`Unique option names: ${Object.keys(allOptions).length}\n`);

  // Sort by size
  const bySize = Object.entries(allOptions)
    .sort((a, b) => (b[1].valueLength || 0) - (a[1].valueLength || 0));

  console.log('Top 20 Options by Size:');
  console.log('================================================\n');
  bySize.slice(0, 20).forEach(([name, opt], idx) => {
    const type = opt.isSerialized ? '[SERIALIZED]' : opt.isJson ? '[JSON]' : '[TEXT]';
    console.log(`${idx + 1}. ${name} ${type}`);
    console.log(`   Size: ${(opt.valueLength / 1024).toFixed(2)} KB, Autoload: ${opt.autoload}`);
  });

  // Extract critical WordPress options
  const criticalOptions = {};
  const criticalKeys = [
    'siteurl', 'home', 'blogname', 'blogdescription', 'admin_email',
    'users_can_register', 'permalink_structure', 'timezone_string',
    'gmt_offset', 'date_format', 'time_format'
  ];

  criticalKeys.forEach(key => {
    if (allOptions[key]) {
      criticalOptions[key] = allOptions[key];
    }
  });

  console.log(`\n\nCritical WordPress Settings:`);
  console.log('================================================\n');
  Object.entries(criticalOptions).forEach(([name, opt]) => {
    console.log(`${name}: ${opt.optionValue}`);
  });

  // Save files
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-options-all.json'),
    JSON.stringify({
      timestamp: new Date().toISOString(),
      totalOptions: totalRows,
      uniqueNames: Object.keys(allOptions).length,
      data: allOptions
    }, null, 2)
  );

  // Save by category
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-options-by-category.json'),
    JSON.stringify({
      wordpress: Object.keys(optionGroups.wordpress).length,
      plugins: Object.keys(optionGroups.plugins).length,
      theme: Object.keys(optionGroups.theme).length,
      seo: Object.keys(optionGroups.seo).length,
      cache: Object.keys(optionGroups.cache).length,
      forms: Object.keys(optionGroups.forms).length,
      other: Object.keys(optionGroups.other).length,
      data: optionGroups
    }, null, 2)
  );

  // Save critical settings
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-options-critical.json'),
    JSON.stringify({
      description: 'Critical WordPress site settings',
      data: criticalOptions
    }, null, 2)
  );

  // Extract plugin-specific settings
  const pluginSettings = {};
  Object.entries(allOptions).forEach(([name, opt]) => {
    if (name.includes('elementor') || name.includes('yoast') ||
        name.includes('rank_math') || name.includes('wpcode') ||
        name.includes('forminator') || name.includes('litespeed') ||
        name.includes('astra')) {
      pluginSettings[name] = opt;
    }
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'wp-options-plugins.json'),
    JSON.stringify({
      description: 'Plugin-specific settings and configurations',
      count: Object.keys(pluginSettings).length,
      data: pluginSettings
    }, null, 2)
  );

  console.log(`\n\nFiles saved:`);
  console.log(`  ✓ wp-options-all.json (${totalRows} options)`);
  console.log(`  ✓ wp-options-by-category.json (7 categories)`);
  console.log(`  ✓ wp-options-critical.json (${Object.keys(criticalOptions).length} critical settings)`);
  console.log(`  ✓ wp-options-plugins.json (${Object.keys(pluginSettings).length} plugin settings)`);

} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
