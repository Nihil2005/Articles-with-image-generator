'use client'

import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ArticleForm = () => {
  const [topicTitle, setTopicTitle] = useState('');
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/generate_article/', { topic_title: topicTitle });
      const formattedArticle = formatArticleWithImages(response.data.article);
      setArticle(formattedArticle);
    } catch (error) {
      console.error('Error generating article:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatArticleWithImages = (articleText) => {
    // Regex to identify URLs in the article text
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    // Split article text by URLs and format them as Markdown images
    const parts = articleText.split(urlRegex);
    return parts.map((part, index) =>
      urlRegex.test(part) ? `![Image](${part})` : part
    ).join('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Generate Article with Images</h1>
      <form onSubmit={handleSubmit} className="mb-8">
        <input
          type="text"
          placeholder="Enter topic title"
          value={topicTitle}
          onChange={(e) => setTopicTitle(e.target.value)}
          required
          className="w-full px-4 py-2 text-black rounded-md border border-gray-300 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none"
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </form>
      {article && (
        <div className="flex  flex-col p-2 gap-3">
          <ReactMarkdown className=''
            components={{
              h2: ({ node, ...props }) => <h1 {...props} className="text-2xl font-bold mb-4 mt-6 leading-snug" />,
              strong: ({ node, ...props }) => <strong {...props} className="font-bold text-2xl" />,
              p: ({ node, ...props }) => <p {...props} className="tex-xl" />,
              img: ({ node, ...props }) => <img {...props} className="w-full md:w-2/3 mx-auto rounded-lg shadow-md shadow-slate-500" alt="Article Image" />,
              a: ({ node, ...props }) => <a {...props} className="text-blue-500 hover:underline" />,
            }}
          >
            {article}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};

export default ArticleForm;
