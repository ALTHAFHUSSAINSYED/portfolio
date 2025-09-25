import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the context
const ThemeContext = createContext();

// Create a provider component
export const ThemeProvider = ({ children }) => {
  // ✨ MODIFIED: Theme now ALWAYS defaults to 'dark' on initial load.
  const [theme, setTheme] = useState('dark');

  // This effect runs only once to apply the default dark theme.
  useEffect(() => {
    const body = window.document.body;
    const html = window.document.documentElement;
    body.classList.add('dark');
    html.classList.add('dark');

    // ✨ NEW: Optional smooth transition for theme toggle
    body.style.transition = 'background-color 0.4s ease, color 0.4s ease';
  }, []); // Empty dependency array ensures this runs only once.

  const toggleTheme = () => {
    setTheme(prevTheme => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      
      // ✨ MODIFIED: Update classes on both body and html to affect root scrollbar
      const body = window.document.body;
      const html = window.document.documentElement;
      body.classList.remove('light', 'dark');
      html.classList.remove('light', 'dark');
      body.classList.add(newTheme);
      html.classList.add(newTheme);

      // ✨ NEW: Ensure smoother transition even after toggle
      body.style.transition = 'background-color 0.4s ease, color 0.4s ease';
      
      return newTheme;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context easily
export const useTheme = () => {
  return useContext(ThemeContext);
};
