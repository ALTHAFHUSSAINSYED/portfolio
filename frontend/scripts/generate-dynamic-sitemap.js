const axios = require('axios');
const fs = require('fs');
const path = require('path');

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';
const siteUrl = 'https://www.althafportfolio.site';

// Generate dynamic sitemap from live data
const generateDynamicSitemap = async () => {
  try {
    console.log('🔍 Fetching blogs from S3 bucket via API...');
    
    // Fetch blogs from backend API (which reads from S3)
    const response = await axios.get(`${API_BASE_URL}/api/blogs`);
    const blogs = response.data || [];
    
    console.log(`✅ Found ${blogs.length} blogs from S3`);

    // Static pages
    const staticPages = [
      { url: '/', priority: '1.0', changefreq: 'weekly' },
      { url: '/#about', priority: '0.8', changefreq: 'monthly' },
      { url: '/#projects', priority: '0.8', changefreq: 'weekly' },
      { url: '/#blogs', priority: '0.9', changefreq: 'daily' },
      { url: '/#contact', priority: '0.7', changefreq: 'monthly' },
    ];

    // Dynamic blog pages from S3
    const blogPages = blogs
      .filter(blog => blog.published !== false && blog.id)
      .map(blog => ({
        url: `/blogs/${blog.id}`,
        priority: '0.9',
        changefreq: 'weekly',
        lastmod: blog.created_at 
          ? new Date(blog.created_at).toISOString().split('T')[0] 
          : new Date().toISOString().split('T')[0]
      }));

    // Fetch projects from MongoDB
    console.log('🔍 Fetching projects from MongoDB...');
    const projectsResponse = await axios.get(`${API_BASE_URL}/api/projects`);
    const projects = projectsResponse.data || [];
    
    console.log(`✅ Found ${projects.length} projects from MongoDB`);

    // Dynamic project pages
    const projectPages = projects
      .filter(project => project._id || project.id)
      .map(project => ({
        url: `/projects/${project._id || project.id}`,
        priority: '0.8',
        changefreq: 'monthly',
        lastmod: new Date().toISOString().split('T')[0]
      }));

    const allPages = [...staticPages, ...blogPages, ...projectPages];

    // Generate XML sitemap
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
    
    console.log('\n✅ Dynamic sitemap generated successfully!');
    console.log(`   📊 Total URLs: ${allPages.length}`);
    console.log(`   - ${staticPages.length} static pages`);
    console.log(`   - ${blogPages.length} blog posts (from S3)`);
    console.log(`   - ${projectPages.length} projects (from MongoDB)`);
    console.log(`   📍 Location: ${sitemapPath}`);
    console.log(`   🌐 Submit to: https://search.google.com/search-console`);
  } catch (error) {
    console.error('❌ Error generating dynamic sitemap:', error.message);
    
    // Fallback: Use local blogs.json if API fails
    console.log('⚠️  Falling back to local blogs.json...');
    const blogsPath = path.join(__dirname, '../public/data/blogs.json');
    
    if (fs.existsSync(blogsPath)) {
      const blogsData = JSON.parse(fs.readFileSync(blogsPath, 'utf8'));
      const blogs = Array.isArray(blogsData) ? blogsData : (blogsData.blogs || []);
      
      const staticPages = [
        { url: '/', priority: '1.0', changefreq: 'weekly' },
        { url: '/#about', priority: '0.8', changefreq: 'monthly' },
        { url: '/#projects', priority: '0.8', changefreq: 'weekly' },
        { url: '/#blogs', priority: '0.9', changefreq: 'daily' },
        { url: '/#contact', priority: '0.7', changefreq: 'monthly' },
      ];

      const blogPages = blogs
        .filter(blog => blog.published !== false && blog.id)
        .map(blog => ({
          url: `/blogs/${blog.id}`,
          priority: '0.9',
          changefreq: 'weekly',
          lastmod: blog.created_at 
            ? new Date(blog.created_at).toISOString().split('T')[0] 
            : new Date().toISOString().split('T')[0]
        }));

      const allPages = [...staticPages, ...blogPages];

      const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allPages.map(page => `  <url>
    <loc>${siteUrl}${page.url}</loc>${page.lastmod ? `
    <lastmod>${page.lastmod}</lastmod>` : ''}
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

      const sitemapPath = path.join(__dirname, '../public/sitemap.xml');
      fs.writeFileSync(sitemapPath, sitemap);
      
      console.log(`✅ Fallback sitemap generated with ${allPages.length} URLs`);
    } else {
      console.error('❌ No fallback data available');
      process.exit(1);
    }
  }
};

generateDynamicSitemap();
