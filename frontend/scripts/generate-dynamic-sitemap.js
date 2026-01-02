const fs = require('fs');
const path = require('path');
const https = require('https');

const API_URL = "https://api.althafportfolio.site/api/blogs";
const SITEMAP_PATH = path.join(__dirname, '../public/sitemap.xml');
const DOMAIN = 'https://althafportfolio.site';

// 1. Static Pages List
const staticPages = ['', '/about', '/projects', '/blogs', '/contact'];

const generateSitemap = () => {
  console.log("🔍 Generating sitemap...");

  https.get(API_URL, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      let blogs = [];
      try {
        const json = JSON.parse(data);
        // Handle various API response formats safely
        blogs = Array.isArray(json) ? json : (json.data || json.blogs || []);
      } catch (e) {
        console.warn("⚠️ API returned invalid JSON. Using empty blog list.");
      }

      const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${staticPages.map(page => `
  <url>
    <loc>${DOMAIN}${page}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`).join('')}
  ${blogs.map(blog => `
  <url>
    <loc>${DOMAIN}/blogs/${blog.id}</loc>
    <lastmod>${blog.date || new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>`).join('')}
</urlset>`;

      fs.writeFileSync(SITEMAP_PATH, sitemapContent);
      console.log("✅ Sitemap generated successfully!");
    });
  }).on('error', (err) => {
    console.error("❌ API Request failed. Generating static-only sitemap.");
    // Generate basic sitemap if API fails so build doesn't break
    const basicSitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${staticPages.map(page => `<url><loc>${DOMAIN}${page}</loc></url>`).join('')}
</urlset>`;
    fs.writeFileSync(SITEMAP_PATH, basicSitemap);
  });
};

generateSitemap();
