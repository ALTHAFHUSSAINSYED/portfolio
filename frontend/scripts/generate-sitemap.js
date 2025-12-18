const fs = require('fs');
const path = require('path');

// Read blogs.json
const blogsPath = path.join(__dirname, '../public/data/blogs.json');
const blogsData = JSON.parse(fs.readFileSync(blogsPath, 'utf8'));
const blogs = Array.isArray(blogsData) ? blogsData : (blogsData.blogs || []);

const siteUrl = 'https://www.althafportfolio.site';

// Generate sitemap XML
const generateSitemap = () => {
  const staticPages = [
    { url: '/', priority: '1.0', changefreq: 'weekly' },
    { url: '/#about', priority: '0.8', changefreq: 'monthly' },
    { url: '/#projects', priority: '0.8', changefreq: 'weekly' },
    { url: '/#blogs', priority: '0.9', changefreq: 'daily' },
    { url: '/#contact', priority: '0.7', changefreq: 'monthly' },
  ];

  const blogPages = blogs
    .filter(blog => blog.published !== false)
    .map(blog => ({
      url: `/blogs/${blog.id}`,
      priority: '0.9',
      changefreq: 'weekly',
      lastmod: blog.created_at ? new Date(blog.created_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
    }));

  const allPages = [...staticPages, ...blogPages];

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
${allPages.map(page => `  <url>
    <loc>${siteUrl}${page.url}</loc>${page.lastmod ? `
    <lastmod>${page.lastmod}</lastmod>` : ''}
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  // Write to public folder
  const sitemapPath = path.join(__dirname, '../public/sitemap.xml');
  fs.writeFileSync(sitemapPath, sitemap);
  console.log(`✅ Sitemap generated with ${allPages.length} URLs`);
  console.log(`   - ${staticPages.length} static pages`);
  console.log(`   - ${blogPages.length} blog posts`);
  console.log(`   📍 Location: ${sitemapPath}`);
};

generateSitemap();
