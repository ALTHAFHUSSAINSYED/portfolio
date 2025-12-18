import React, { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';

const BlogForm = ({ onSubmit, initialData, onCancel }) => {
  const [title, setTitle] = useState(initialData?.title || '');
  const [summary, setSummary] = useState(initialData?.summary || '');
  const [content, setContent] = useState(initialData?.content || '');
  const [category, setCategory] = useState(initialData?.category || '');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ title, summary, content, category });
  };

  return (
    <Card className="p-6 mb-8">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="blog-title" className="block font-semibold mb-1">Title</label>
          <input
            type="text"
            id="blog-title"
            name="blog-title"
            autoComplete="off"
            className="w-full border rounded px-3 py-2"
            value={title}
            onChange={e => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="blog-summary" className="block font-semibold mb-1">Summary</label>
          <input
            type="text"
            id="blog-summary"
            name="blog-summary"
            autoComplete="off"
            className="w-full border rounded px-3 py-2"
            value={summary}
            onChange={e => setSummary(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="blog-content" className="block font-semibold mb-1">Content</label>
          <textarea
            id="blog-content"
            name="blog-content"
            autoComplete="off"
            className="w-full border rounded px-3 py-2"
            value={content}
            onChange={e => setContent(e.target.value)}
            rows={5}
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="blog-category" className="block font-semibold mb-1">Category</label>
          <input
            type="text"
            id="blog-category"
            name="blog-category"
            autoComplete="off"
            className="w-full border rounded px-3 py-2"
            value={category}
            onChange={e => setCategory(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button type="submit" className="bg-cyan-500 text-white">{initialData ? 'Update' : 'Create'} Blog</Button>
          {onCancel && <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>}
        </div>
      </form>
    </Card>
  );
};

export default BlogForm;
