import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Search, X, Calendar, ArrowRight, Tag, BookOpen, AlertCircle } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

const BlogsSection = () => {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  const navigate = useNavigate();
  const location = useLocation();

  // 1. Fetch Blogs
  useEffect(() => {
    const fetchBlogs = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/blogs`);
        if (!response.ok) throw new Error('Failed to fetch blogs');
        const data = await response.json();
        setBlogs(data);
      } catch (error) {
        console.error('Error fetching blogs:', error);
        setBlogs([]);
      } finally {
        setLoading(false);
      }
    };
    fetchBlogs();
  }, []);

  // 2. Sync URL with State (Handle Dropdown Navigation)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const categoryParam = params.get('category');
    if (categoryParam) {
      setSelectedCategory(categoryParam);
      // Optional: Scroll to section if needed
      document.getElementById('blogs')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [location.search]);

  // 3. Extract Unique Categories (from ALL blogs, ignoring filters)
  const categories = [...new Set(blogs.flatMap(blog => 
    blog.category ? [blog.category] : []
  ))].sort();

  // 4. ROBUST FILTERING LOGIC
  const filteredBlogs = blogs.filter(blog => {
    // A. Search Filter (Checks Title, Summary, AND Tags)
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch = !query || 
      blog.title.toLowerCase().includes(query) ||
      blog.summary.toLowerCase().includes(query) ||
      (blog.tags && blog.tags.some(tag => tag.toLowerCase().includes(query)));

    // B. Category Filter
    const matchesCategory = !selectedCategory || blog.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // 5. Clear All Filters Handler
  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory(null);
    navigate('/', { replace: true }); // Clear URL params
  };

  const handleCategoryClick = (category) => {
    if (selectedCategory === category) {
      setSelectedCategory(null);
      navigate('/', { replace: true });
    } else {
      setSelectedCategory(category);
      // Update URL without reloading
      navigate(`/?category=${encodeURIComponent(category)}`, { replace: true });
    }
  };

  return (
    <section id="blogs" className="py-20 bg-background relative min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header Section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-foreground flex items-center justify-center">
            <BookOpen className="w-8 h-8 mr-3 text-cyan-soft" />
            Technical Insights
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Exploring the frontiers of DevOps, Cloud Computing, and AI through detailed technical articles.
          </p>
        </div>

        {/* Search and Filter Controls */}
        <div className="mb-10 space-y-6">
          
          {/* Search Bar */}
          <div className="max-w-xl mx-auto relative">
            <div className="relative group">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground group-hover:text-cyan-soft transition-colors" />
              <Input
                type="text"
                placeholder="Search articles (e.g., 'DevOps', 'AWS', 'Security')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-10 py-6 bg-secondary/30 border-border focus:border-cyan-400/50 text-lg rounded-xl transition-all shadow-sm"
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-red-400 p-1"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Categories List (Always Visible) */}
          <div className="flex flex-wrap justify-center gap-2">
            <Button
              variant={selectedCategory === null ? "default" : "outline"}
              onClick={() => handleCategoryClick(null)}
              className={`rounded-full px-4 ${selectedCategory === null ? 'bg-cyan-500 hover:bg-cyan-600 text-white border-0' : 'hover:border-cyan-400 hover:text-cyan-soft'}`}
            >
              All
            </Button>
            {categories.map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "default" : "outline"}
                onClick={() => handleCategoryClick(cat)}
                className={`rounded-full px-4 transition-all duration-300 ${
                  selectedCategory === cat 
                    ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white border-0 shadow-lg' 
                    : 'hover:border-pink-400 hover:text-pink-soft'
                }`}
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>

        {/* Results Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading articles...</p>
          </div>
        ) : filteredBlogs.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredBlogs.map((blog) => (
              <Card 
                key={blog._id || blog.id} 
                className="flex flex-col h-full overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-border/50 bg-card/50 backdrop-blur-sm group"
              >
                {/* Blog Image (Optional - Placeholder logic) */}
                <div className="h-48 bg-gradient-to-br from-gray-800 to-gray-900 relative overflow-hidden">
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors duration-500" />
                  <div className="absolute bottom-4 left-4">
                    <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 hover:bg-cyan-500/20 backdrop-blur-md">
                      {blog.category || 'Tech'}
                    </Badge>
                  </div>
                </div>

                <div className="p-6 flex flex-col flex-grow">
                  <div className="flex items-center text-xs text-muted-foreground mb-3 space-x-4">
                    <span className="flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      {new Date(blog.createdAt || blog.date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center">
                      <Tag className="w-3 h-3 mr-1" />
                      {blog.tags ? blog.tags.length : 0} tags
                    </span>
                  </div>

                  <h3 className="text-xl font-bold mb-3 text-foreground line-clamp-2 group-hover:text-cyan-soft transition-colors">
                    {blog.title}
                  </h3>
                  
                  <p className="text-muted-foreground text-sm mb-6 line-clamp-3 flex-grow">
                    {blog.summary}
                  </p>

                  <div className="mt-auto pt-4 border-t border-border/30 flex justify-between items-center">
                    <a 
                      href={`/blog/${blog._id || blog.id}`} 
                      className="text-sm font-semibold text-cyan-soft hover:text-pink-soft transition-colors flex items-center"
                    >
                      Read Article <ArrowRight className="w-4 h-4 ml-1" />
                    </a>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          /* No Results State */
          <div className="text-center py-20 bg-secondary/10 rounded-2xl border border-dashed border-border">
            <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
            <h3 className="text-xl font-bold text-foreground mb-2">No blogs found</h3>
            <p className="text-muted-foreground mb-6">
              We couldn't find any articles matching "{searchQuery}"
              {selectedCategory && ` in ${selectedCategory}`}.
            </p>
            <Button 
              onClick={clearFilters}
              variant="outline"
              className="border-cyan-400/50 text-cyan-soft hover:bg-cyan-400/10"
            >
              Clear all filters
            </Button>
          </div>
        )}
      </div>
    </section>
  );
};

export default BlogsSection;
