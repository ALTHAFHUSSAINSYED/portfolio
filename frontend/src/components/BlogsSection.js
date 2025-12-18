import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Bookmark, Newspaper, RefreshCw, Filter, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

const BlogsSection = () => {
  const [blogs, setBlogs] = useState([]);
  const [allBlogs, setAllBlogs] = useState([]); // Keep original blogs for reset
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showCategoryFilter, setShowCategoryFilter] = useState(true); // VISIBLE BY DEFAULT
  const [visibleCount, setVisibleCount] = useState(3);
  const sectionRef = useRef(null);
  const location = useLocation();
  
  // ONLY THESE 6 CATEGORIES ALLOWED - ALL OTHERS PERMANENTLY REMOVED
  const allowedCategories = [
    'Low-Code/No-Code',
    'Cybersecurity',
    'Software Development',
    'DevOps',
    'AI and ML',
    'Cloud Computing'
  ];

  useEffect(() => {
    fetchBlogs();
  }, []);
  
  // Check URL for category parameter
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const categoryParam = searchParams.get('category');
    
    if (categoryParam && allowedCategories.includes(categoryParam)) {
      setSelectedCategory(categoryParam);
      setVisibleCount(3);
    }
  }, [location.search]);
  
  // Reset visible count when filters change
  useEffect(() => {
    setVisibleCount(3);
  }, [selectedCategory, searchQuery]);

  const fetchBlogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs`);
      if (response.ok) {
        const data = await response.json();
        // Filter to ONLY show allowed categories
        const filteredData = data.filter(blog => 
          blog.category && allowedCategories.includes(blog.category)
        );
        // Sort by date (newest first)
        const sortedBlogs = [...filteredData].sort((a, b) => {
          const dateA = new Date(a.created_at || a.date || 0);
          const dateB = new Date(b.created_at || b.date || 0);
          return dateB - dateA;
        });
        setBlogs(sortedBlogs);
        setAllBlogs(sortedBlogs);
        setError(null);
      } else {
        throw new Error('Failed to fetch blogs');
      }
    } catch (err) {
      console.error('Error fetching blogs:', err);
      setError(err.message);
      // Try local fallback
      try {
        const localData = await import('../../public/data/blogs.json');
        const filteredData = (localData.default || []).filter(blog => 
          blog.category && allowedCategories.includes(blog.category)
        );
        setBlogs(filteredData);
        setAllBlogs(filteredData);
      } catch (e) {
        setBlogs([]);
        setAllBlogs([]);
      }
    } finally {
      setLoading(false);
    }
  };

  // CASE-INSENSITIVE SEARCH: title, summary, tags, category
  const handleSearch = (query) => {
    setSearchQuery(query);
    const lowerQuery = query.toLowerCase().trim();
    
    if (!lowerQuery) {
      setBlogs(allBlogs);
      return;
    }
    
    const filtered = allBlogs.filter(blog => {
      const titleMatch = blog.title?.toLowerCase().includes(lowerQuery);
      const summaryMatch = blog.summary?.toLowerCase().includes(lowerQuery);
      const categoryMatch = blog.category?.toLowerCase().includes(lowerQuery);
      const tagsMatch = blog.tags?.some(tag => tag.toLowerCase().includes(lowerQuery));
      
      return titleMatch || summaryMatch || categoryMatch || tagsMatch;
    });
    
    setBlogs(filtered);
  };

  // Clear all filters
  const clearAllFilters = () => {
    setSearchQuery('');
    setSelectedCategory(null);
    setBlogs(allBlogs);
    setVisibleCount(3);
    window.history.pushState({}, '', window.location.pathname);
  };

  // Get filtered blogs for display
  const displayBlogs = selectedCategory 
    ? blogs.filter(blog => blog.category === selectedCategory)
    : blogs;

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
            {/* Search Bar */}
            <input
              type="text"
              placeholder="Search blogs..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-56 max-w-xs px-4 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
            />
            {/* Clear All Filters - LEFT SIDE */}
            {(searchQuery || selectedCategory) && (
              <Button 
                onClick={clearAllFilters}
                variant="outline" 
                className="flex items-center gap-2 border-red-500 text-red-500 hover:bg-red-500/10"
              >
                <X className="w-4 h-4" />
                Clear All Filters
              </Button>
            )}
          </div>
          
          {/* Category Filter - VISIBLE BY DEFAULT */}
          {showCategoryFilter && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Filter by Category:</h3>
              <div className="flex flex-wrap gap-3 justify-center">
                {allowedCategories.map((category) => (
                  <Badge 
                    key={category}
                    onClick={() => {
                      if (selectedCategory === category) {
                        setSelectedCategory(null);
                      } else {
                        setSelectedCategory(category);
                      }
                    }}
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
        ) : displayBlogs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">
              {searchQuery || selectedCategory 
                ? 'No blogs found matching your filters.' 
                : 'No blogs available yet.'}
            </p>
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
            {searchQuery && (
              <div className="mb-6 text-center">
                <p className="text-primary font-medium">
                  Search results for: <span className="font-bold">"{searchQuery}"</span>
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {displayBlogs
                .slice(0, visibleCount)
                .map((blog, idx) => (
                  <Card key={blog.id || blog._id || idx} className="flex flex-col overflow-hidden transition-all duration-300 backdrop-blur-sm hover:shadow-lg hover:shadow-cyan-500/20 group border-border/40 h-auto">
                    {/* Compact Header with Badge and Date */}
                    <div className="p-4 pb-2">
                      <div className="flex justify-between items-start mb-2">
                        <Badge className="bg-cyan-500/10 text-cyan-300 border-cyan-500/30 text-xs px-2 py-0.5">
                          {blog.category}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground flex items-center">
                          <Calendar className="w-3 h-3 mr-1" /> 
                          {blog.created_at && new Date(blog.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                      </div>

                      {/* Title - Bold and Eye-catching */}
                      <h3 className="text-lg font-bold text-foreground leading-snug group-hover:text-cyan-soft transition-colors line-clamp-2 mb-2">
                        {blog.title}
                      </h3>
                    </div>

                    {/* Multi-line Attractive Teaser (2-3 lines) */}
                    <div className="px-4 pb-3 flex-grow">
                      <p className="text-muted-foreground text-sm line-clamp-3 leading-relaxed">
                        {blog.summary}
                      </p>
                    </div>

                    {/* Compact Footer with Read More */}
                    <div className="px-4 py-2 bg-secondary/10 border-t border-white/5 mt-auto">
                      <Link
                        to={`/blogs/${blog.id || blog._id}`}
                        className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors flex items-center uppercase tracking-wider"
                      >
                        Read More <Bookmark className="w-3 h-3 ml-2" />
                      </Link>
                    </div>
                  </Card>
                ))}
            </div>
          </>
        )}

        {/* Dynamic "See More" / "See Less" Button */}
        {(() => {
          const totalFiltered = displayBlogs.length;
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
                    // Scroll to blogs section smoothly
                    document.getElementById('blogs')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
