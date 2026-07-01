const fs = require('fs');
const path = require('path');

// Load attachments from Task 1 output
const attachments = JSON.parse(fs.readFileSync('tmp/attachments.json', 'utf8'));

// Scan local images directory to create full path mapping
function scanLocalImages(dir, baseDir = '') {
  const localFiles = {};
  const items = fs.readdirSync(dir, { withFileTypes: true });

  items.forEach(item => {
    const fullPath = path.join(dir, item.name);
    const relativePath = baseDir ? `${baseDir}/${item.name}` : item.name;

    if (item.isDirectory()) {
      Object.assign(localFiles, scanLocalImages(fullPath, relativePath));
    } else if (item.isFile()) {
      const ext = path.extname(item.name).toLowerCase();
      if (['.jpg', '.jpeg', '.png', '.webp', '.gif'].includes(ext)) {
        localFiles[item.name] = `/images/${relativePath}`;
      }
    }
  });

  return localFiles;
}

const localImages = scanLocalImages('images');

// Build mapping: WordPress URL → local path
const imageMap = {};
const urlsByFilename = {}; // Track which URLs use each filename
let foundLocalCount = 0;

attachments.forEach(att => {
  const wpUrl = att.url;
  const fileName = path.basename(wpUrl); // Extract filename from URL

  // Try to find matching local file
  const localPath = localImages[fileName] || `/images/${fileName}`;

  if (localImages[fileName]) {
    foundLocalCount++;
  }

  imageMap[wpUrl] = localPath;

  // Track filename collisions
  if (!urlsByFilename[fileName]) {
    urlsByFilename[fileName] = [];
  }
  urlsByFilename[fileName].push(wpUrl);
});

// Write mapping to file
fs.writeFileSync('tmp/image-map.json', JSON.stringify(imageMap, null, 2));

// Report statistics
const uniqueFilenames = Object.keys(urlsByFilename).length;
const collisions = Object.entries(urlsByFilename).filter(([, urls]) => urls.length > 1).length;

console.log(`✓ Created image map for ${Object.keys(imageMap).length} attachment URLs`);
console.log(`  - Unique filenames: ${uniqueFilenames}`);
console.log(`  - Found in local images/: ${foundLocalCount} (${((foundLocalCount / Object.keys(imageMap).length) * 100).toFixed(1)}%)`);
console.log(`  - Total local image files: ${Object.keys(localImages).length}`);
console.log(`  - Filename collisions: ${collisions}`);

if (collisions > 0) {
  console.log('\nCollisions (same filename, different sources):');
  Object.entries(urlsByFilename)
    .filter(([, urls]) => urls.length > 1)
    .slice(0, 5) // Show first 5
    .forEach(([filename, urls]) => {
      console.log(`  ${filename}: ${urls.length} sources`);
    });
}
