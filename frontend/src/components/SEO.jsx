import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEO = ({
  title = 'Althaf Hussain | DevOps Engineer & Cloud Architect',
  description = 'Portfolio of Althaf Hussain Syed - Expert DevOps Engineer specializing in AWS, Azure, Kubernetes, CI/CD pipelines, Infrastructure as Code, and Cloud Architecture. Explore projects, blogs, and technical expertise.',
  keywords = 'DevOps Engineer, Cloud Architect, AWS Certified, Azure Expert, Kubernetes, Docker, CI/CD, Terraform, Infrastructure as Code, Cloud Computing, DevOps Portfolio, Site Reliability Engineering, Container Orchestration, Microservices, Cloud Native',
  url = 'https://althafportfolio.site',
  image = 'https://althafportfolio.site/profile-pic.jpg',
  type = 'website',
  author = 'Althaf Hussain Syed',
  twitterHandle = '@althafhussain',
  canonicalUrl,
  publishedTime,
  modifiedTime,
  tags = [],
  structuredData
}) => {
  const siteUrl = 'https://althafportfolio.site';
  const defaultImage = `${siteUrl}/profile-pic.jpg`;
  const ogImage = image || defaultImage;
  const pageUrl = canonicalUrl || url;

  // Default structured data for Website schema
  const defaultStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Althaf Hussain - DevOps Engineer Portfolio",
    "description": description,
    "url": siteUrl,
    "author": {
      "@type": "Person",
      "@id": `${siteUrl}/#person`,
      "name": "Althaf Hussain Syed",
      "jobTitle": "DevOps Engineer | Cloud & Infrastructure Engineer",
      "description": "Certified DevOps Engineer with expertise in AWS, Azure, Kubernetes, and Cloud Architecture. Specializing in CI/CD automation, infrastructure as code, and scalable cloud solutions.",
      "url": siteUrl,
      "image": defaultImage,
      "sameAs": [
        "https://www.linkedin.com/in/althafhussainsyed/",
        "https://github.com/ALTHAFHUSSAINSYED"
      ],
      "knowsAbout": [
        "DevOps",
        "Cloud Computing",
        "AWS",
        "Azure",
        "Kubernetes",
        "Docker",
        "CI/CD",
        "Terraform",
        "Infrastructure as Code",
        "Site Reliability Engineering",
        "Microservices",
        "Container Orchestration"
      ],
      "alumniOf": {
        "@type": "CollegeOrUniversity",
        "name": "Your University Name"
      }
    },
    "potentialAction": {
      "@type": "SearchAction",
      "target": `${siteUrl}/?s={search_term_string}`,
      "query-input": "required name=search_term_string"
    }
  };

  const finalStructuredData = structuredData || defaultStructuredData;

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />
      <meta name="robots" content="index, follow" />
      <meta name="language" content="English" />
      <meta name="revisit-after" content="7 days" />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="Althaf Hussain Portfolio" />
      <meta property="og:locale" content="en_US" />

      {/* Article specific Open Graph tags */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && tags.length > 0 && tags.map((tag, idx) => (
        <meta key={`og-tag-${idx}`} property="article:tag" content={tag} />
      ))}
      {type === 'article' && (
        <meta property="article:author" content={author} />
      )}

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={pageUrl} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:creator" content={twitterHandle} />
      <meta name="twitter:site" content={twitterHandle} />

      {/* Canonical URL */}
      <link rel="canonical" href={pageUrl} />

      {/* Additional SEO tags */}
      <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />

      {/* JSON-LD Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify(finalStructuredData)}
      </script>
    </Helmet>
  );
};

export default SEO;
