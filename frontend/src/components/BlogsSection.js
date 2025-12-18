import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Mail, Bookmark, Newspaper, RefreshCw, Filter, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

const BlogsSection = () => {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [customTopic, setCustomTopic] = useState('');
  const [showTopicInput, setShowTopicInput] = useState(false);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showCategoryFilter, setShowCategoryFilter] = useState(false); // Hide filter by default
  const [visibleCount, setVisibleCount] = useState(3); // Progressive loading: start with 3
  const sectionRef = useRef(null);
  const location = useLocation();
  
  // Categories to exclude
  const excludedCategories = [
    'Frontend Development',
    'IoT Development',
    'Blockchain',
    'Databases',
    'Edge Computing',
    'Quantum Computing'
  ];

  useEffect(() => {
    fetchBlogs();
  }, []);
  
  // Extract unique categories from blogs (excluding unwanted ones)
  useEffect(() => {
    if (blogs && blogs.length > 0) {
      const uniqueCategories = [...new Set(
        blogs
          .map(blog => blog.category)
          .filter(cat => cat && !excludedCategories.includes(cat))
      )];
      setCategories(uniqueCategories);
      
      // Get category from URL
      const searchParams = new URLSearchParams(location.search);
      const categoryParam = searchParams.get('category');
      if (categoryParam && uniqueCategories.includes(categoryParam)) {
        setSelectedCategory(categoryParam);
        setVisibleCount(3); // Reset to 3 when category selected
      }
    }
  }, [blogs, location.search]);
  
  // Check URL for category parameter
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const categoryParam = searchParams.get('category');
    
    if (categoryParam) {
      setSelectedCategory(categoryParam);
      setShowCategoryFilter(true);
      setVisibleCount(3); // Reset to 3 when URL category changes
    }
  }, [location.search]);
  
  // Reset visible count when category filter changes
  useEffect(() => {
    setVisibleCount(3); // Always start with 3 blogs
  }, [selectedCategory]);

  const fetchBlogs = async () => {
    setLoading(true);
    try {
      // Try different API endpoints if the main one fails
      const baseUrls = [
        '', // Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000',
        'http://localhost:5001'
      ];
      
      let data = null;
      let succeeded = false;
      
      // Try API endpoints first
      for (const baseUrl of baseUrls) {
        try {
          const response = await fetch(`${baseUrl}/api/blogs`);
          if (response.ok) {
            data = await response.json();
            succeeded = true;
            console.log(`Successfully fetched blogs from ${baseUrl}/api/blogs`);
            break;
          }
        } catch (err) {
          console.log(`Error fetching from ${baseUrl}: ${err.message}`);
        }
      }
      
      // If API endpoints fail, try local JSON file as fallback
      if (!succeeded) {
        try {
          const response = await fetch('/data/blogs.json');
          if (response.ok) {
            const jsonData = await response.json();
            data = jsonData.blogs;
            succeeded = true;
            console.log('Successfully fetched blogs from local JSON file');
          }
        } catch (err) {
          console.log(`Error fetching from local JSON file: ${err.message}`);
        }
      }
      
      if (succeeded && data) {
        // Sort blogs by created_at descending (newest first)
        const sortedBlogs = [...data].sort((a, b) => {
          const dateA = new Date(a.created_at || a.date || 0);
          const dateB = new Date(b.created_at || b.date || 0);
          return dateB - dateA;
        });
        setBlogs(sortedBlogs);
        setError(null);
      } else {
        throw new Error('Failed to fetch blogs from all endpoints');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBlog = async (topic = null) => {
    setGenerating(true);
    try {
      const requestBody = topic ? { topic } : {};
      
      // Try different API endpoints if the main one fails
      const baseUrls = [
        '', // Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000'
      ];
      
      let newBlog = null;
      let succeeded = false;
      
      for (const baseUrl of baseUrls) {
        try {
          const response = await fetch(`${baseUrl}/api/generate-blog`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
          });
          
          if (response.ok) {
            newBlog = await response.json();
            succeeded = true;
            break;
          }
        } catch (err) {
          console.log(`Error generating blog from ${baseUrl}: ${err.message}`);
        }
      }
      
      if (succeeded && newBlog) {
        // Add the new blog to the list and refresh
        setBlogs(prevBlogs => [newBlog, ...prevBlogs]);
        setCustomTopic('');
        setShowTopicInput(false);
      } else {
        throw new Error('Failed to generate blog from all endpoints');
      }
    } catch (err) {
      setError(`Failed to generate blog: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Removed handleDelete function for security

  return (
    <section id="blogs" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Blogs</h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Explore my latest blog posts and AI-generated articles.
          </p>
          
          <div className="mt-6 flex flex-wrap justify-center gap-4">
            <Button 
              onClick={() => fetchBlogs()}
              className="flex items-center gap-2"
              variant="outline"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
            <Button 
              onClick={() => setShowCategoryFilter(!showCategoryFilter)}
              className="flex items-center gap-2"
              variant="secondary"
            >
              <Filter className="w-4 h-4" />
              Categories
            </Button>
            {/* Search utility for existing blogs */}
            <input
              type="text"
              placeholder="Search blogs..."
              className="w-56 max-w-xs px-4 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
              onChange={e => {
                const search = e.target.value.toLowerCase();
                setBlogs(prev => prev.filter(blog => blog.title.toLowerCase().includes(search) || blog.summary.toLowerCase().includes(search)));
              }}
            />
          </div>
          
          {/* Category Filter */}
          {showCategoryFilter && categories.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Filter by Category:</h3>
              <div className="flex flex-wrap gap-3 justify-center">
                {selectedCategory && (
                  <Button 
                    onClick={() => setSelectedCategory(null)}
                    variant="outline" 
                    className="flex items-center gap-2 border-red-500 text-red-500 hover:bg-red-500/10"
                    style={{ display: selectedCategory ? 'flex' : 'none' }}
                  >
                    <X className="w-4 h-4" />
                    Clear Filter
                  </Button>
                )}
                {categories.map((category) => (
                  <Badge 
                    key={category}
                    onClick={() => setSelectedCategory(category === selectedCategory ? null : category)}
                    className={`text-sm px-3 py-1 cursor-pointer hover:opacity-90 ${
                      category === selectedCategory 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-secondary text-secondary-foreground'
                    }`}
                  >
                    {category}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/20 rounded-lg text-center">
            <p className="font-semibold text-red-500 dark:text-red-400">{error}</p>
            <Button 
              onClick={() => fetchBlogs()}
              className="mt-2"
              variant="outline"
              size="sm"
            >
              Try Again
            </Button>
          </div>
        ) : blogs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">No blogs available yet.</p>
          </div>
        ) : (
          <>
            {/* Display filtering information */}
            {selectedCategory && (
              <div className="mb-6 text-center">
                <p className="text-primary font-medium">
                  Showing blogs in category: <span className="font-bold">{selectedCategory}</span>
                </p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {blogs
                .filter(blog => !excludedCategories.includes(blog.category)) // Filter out excluded categories
                .filter(blog => !selectedCategory || blog.category === selectedCategory) // Apply selected category filter
                .slice(0, visibleCount) // Progressive loading
                .map((blog, idx) => (
                  <Card key={blog.id || blog._id || idx} className="p-8 relative block-card hover:shadow-lg transition-all duration-300">
                    <div className="absolute top-4 right-4">
                      <Newspaper className="w-6 h-6 text-cyan-400" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">{blog.title}</h3>
                    <p className="text-muted-foreground mb-4">{blog.summary}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {blog.category && (
                        <Badge variant="default" className="bg-primary text-primary-foreground mr-2 mb-2">
                          {blog.category}
                        </Badge>
                      )}
                      {blog.tags && blog.tags.map((tag, tagIdx) => (
                        <Badge key={tagIdx} variant="secondary" className="mr-2">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground mb-4">
                      {blog.created_at && new Date(blog.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                    <div className="flex justify-end mt-4">
                      <Link 
                        to={`/blogs/${blog.id || blog._id}`} 
                        className="inline-flex items-center px-4 py-2 text-sm font-medium text-cyan-500 hover:text-cyan-600"
                      >
                        Read More
                      </Link>
                    </div>
                  </Card>
                ))}
            </div>
          </>
        )}
        
        {/* Dynamic "See More" / "See Less" Button */}
        {(() => {
          const filteredBlogs = blogs
            .filter(blog => !excludedCategories.includes(blog.category))
            .filter(blog => !selectedCategory || blog.category === selectedCategory);
          
          const totalFiltered = filteredBlogs.length;
          const allVisible = visibleCount >= totalFiltered;
          
          // Only show button if there are more than 3 blogs
          if (totalFiltered <= 3) return null;
          
          if (allVisible) {
            // Show "See Less Blogs" button
            return (
              <div className="mt-12 text-center">
                <Button 
                  variant="outline" 
                  className="glassmorphic-btn"
                  onClick={() => {
                    setVisibleCount(3);
                    setSelectedCategory(null); // Clear filter
                    setShowCategoryFilter(false); // Hide category filter
                  }}
                >
                  See Less Blogs
                </Button>
              </div>
            );
          } else {
            // Show "See More Blogs" button
            return (
              <div className="mt-12 text-center">
                <Button 
                  variant="outline" 
                  className="glassmorphic-btn"
                  onClick={() => setVisibleCount(prev => prev + 3)}
                >
                  See More Blogs
                </Button>
              </div>
            );
          }
        })()}
      </div>
    </section>
  );
};

export default BlogsSection;
