import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const useManualScroll = () => {
  const location = useLocation();

  // This effect runs after every navigation.
  useEffect(() => {
    // Try to find a saved scroll position for the current page.
    const savedPosition = sessionStorage.getItem(`scrollPos:${location.pathname}`);

    if (savedPosition) {
      // If a position was found, scroll to it.
      window.scrollTo(0, parseInt(savedPosition, 10));
      // We don't remove it, so it's available if you navigate back and forth.
    } else {
      // If no position was found, scroll to the top of the page.
      window.scrollTo(0, 0);
    }

    // This function runs when you are about to navigate AWAY from the page.
    const handleBeforeUnload = () => {
      // It saves the current scroll position associated with the current path.
      sessionStorage.setItem(`scrollPos:${location.pathname}`, window.scrollY);
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // The cleanup function for the effect.
    return () => {
      // This is crucial: before the component unmounts (i.e., before you navigate away),
      // we save the current scroll position.
      sessionStorage.setItem(`scrollPos:${location.pathname}`, window.scrollY);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [location.pathname]); // This effect depends only on the page's path.
};

export default useManualScroll;
