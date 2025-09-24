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
    body.classList.add('dark');
  }, []); // Empty dependency array ensures this runs only once.

  const toggleTheme = () => {
    setTheme(prevTheme => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      
      // ✨ MODIFIED: Logic is simplified to only update the class for the current session.
      // No localStorage is used.
      const body = window.document.body;
      body.classList.remove('light', 'dark');
      body.classList.add(newTheme);
      
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
