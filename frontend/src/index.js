// src/index.js

import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { ThemeProvider } from "./context/ThemeContext";
// ✨ MODIFIED: Import the tools for the new router setup
import { createBrowserRouter, RouterProvider } from "react-router-dom";
// Import the smooth scroll functionality
import "./smooth-scroll";
import { Loader2 } from "lucide-react";

// ✨ CODE SPLITTING: Lazy load route components for better performance
const Portfolio = lazy(() => import("./components/Portfolio"));
const ProjectDetailPage = lazy(() => import("./components/ProjectDetailPage"));
const BlogDetailPage = lazy(() => import("./components/BlogDetailPage"));

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <div className="text-center">
      <Loader2 className="w-12 h-12 mx-auto animate-spin text-cyan-soft" />
      <p className="mt-4 text-muted-foreground">Loading...</p>
    </div>
  </div>
);

// ✨ NEW: Define the application routes using the modern object-based approach
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />, // The App component is now the main layout
    children: [
      {
        index: true, // The Portfolio component renders at the "/" path
        element: (
          <Suspense fallback={<PageLoader />}>
            <Portfolio />
          </Suspense>
        ),
      },
      {
        path: "/projects/:projectId", // The detail page renders at its specific path
        element: (
          <Suspense fallback={<PageLoader />}>
            <ProjectDetailPage />
          </Suspense>
        ),
      },
      {
        path: "/blogs/:blogId", // Blog detail page route
        element: (
          <Suspense fallback={<PageLoader />}>
            <BlogDetailPage />
          </Suspense>
        ),
      },
    ],
  },
]);

const rootElement = document.getElementById("root");

// Support hydration for pre-rendered content (react-snap)
if (rootElement.hasChildNodes()) {
  ReactDOM.hydrateRoot(
    rootElement,
    <React.StrictMode>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </React.StrictMode>
  );
} else {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </React.StrictMode>
  );
}
