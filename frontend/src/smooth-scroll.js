// smooth-scroll.js
// Enhanced smooth scrolling functionality specifically for the contact button

/**
 * Initialize smooth scrolling functionality for the contact button in the header.
 * This provides an enhanced scrolling experience with better positioning and easing.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Wait for full DOM render
  setTimeout(() => {
    initContactScrollHandler();
  }, 300);
});

/**
 * Initialize the contact button scroll functionality with improved selection and error handling
 */
let retryCount = 0;
const MAX_RETRIES = 5;

function initContactScrollHandler() {
  // More robust selector targeting both ID and button content
  const contactButtons = document.querySelectorAll('#contact-nav-button, #contact-nav-button-mobile, button[id*="contact"]');
  const contactSection = document.getElementById('contact');

  if (contactButtons.length > 0 && contactSection) {
    contactButtons.forEach(button => {
      // Remove any existing click listeners first to prevent duplicates
      button.removeEventListener('click', handleContactButtonClick);
      // Add fresh click listener
      button.addEventListener('click', handleContactButtonClick);
    });

    console.log(`Contact button scroll handlers initialized (${contactButtons.length} buttons found)`);
    retryCount = 0; // Reset on success
  } else {
    if (retryCount < MAX_RETRIES) {
      retryCount++;
      console.warn(`Contact button or section not found, retrying in 500ms (Attempt ${retryCount}/${MAX_RETRIES})`);
      setTimeout(initContactScrollHandler, 500);
    } else {
      console.warn('Contact scroll handler initialization stopped after max retries.');
    }
  }
}

/**
 * Handle the contact button click event with improved error handling
 * @param {Event} e - The click event
 */
function handleContactButtonClick(e) {
  // Prevent default behavior
  e.preventDefault();
  console.log('Contact button clicked, scrolling to section');

  const contactSection = document.getElementById('contact');

  if (!contactSection) {
    console.error('Contact section not found');
    return;
  }

  // Get the header height for offset calculation
  const headerHeight = document.querySelector('header')?.offsetHeight || 0;
  const offset = 20; // Extra padding below header

  // Calculate target position with fallbacks
  const targetPosition = contactSection.getBoundingClientRect().top +
    (window.pageYOffset || document.documentElement.scrollTop) -
    headerHeight + offset;

  // Try native smooth scroll first with fallback
  if ('scrollBehavior' in document.documentElement.style) {
    window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
  } else {
    // Use polyfill for browsers without smooth scroll support
    smoothScrollTo(targetPosition, 800);
  }
}

/**
 * Custom smooth scroll implementation with easing and improved fallbacks
 * @param {number} targetPosition - Target scroll position
 * @param {number} duration - Animation duration in milliseconds
 */
function smoothScrollTo(targetPosition, duration) {
  const startPosition = window.pageYOffset || document.documentElement.scrollTop;
  const distance = targetPosition - startPosition;
  let startTime = null;

  // Enhanced easing function for more natural movement
  function easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
  }

  // Animation frame handler with improved error handling
  function animation(currentTime) {
    try {
      if (startTime === null) startTime = currentTime;
      const timeElapsed = currentTime - startTime;
      const nextPosition = easeInOutQuad(timeElapsed, startPosition, distance, duration);

      window.scrollTo(0, nextPosition);

      if (timeElapsed < duration) {
        requestAnimationFrame(animation);
      } else {
        // Final position check to ensure accuracy
        if (Math.abs(window.pageYOffset - targetPosition) > 5) {
          window.scrollTo(0, targetPosition);
        }
        console.log('Scroll animation complete');
      }
    } catch (error) {
      console.error('Error in scroll animation:', error);
      // Emergency fallback
      window.scrollTo(0, targetPosition);
    }
  }

  // Try requestAnimationFrame with multiple fallbacks
  if ('requestAnimationFrame' in window) {
    requestAnimationFrame(animation);
  } else if ('scrollBehavior' in document.documentElement.style) {
    // Modern browsers without rAF but with smooth scroll
    window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
  } else {
    // Legacy fallback with setTimeout
    const step = 25;
    const scrollSteps = Math.abs(Math.floor(distance / step));
    let stepCount = 0;

    const scrollInterval = setInterval(() => {
      if (stepCount >= scrollSteps) {
        clearInterval(scrollInterval);
        window.scrollTo(0, targetPosition);
        return;
      }

      stepCount++;
      const nextPos = easeInOutQuad(stepCount, startPosition, distance, scrollSteps);
      window.scrollTo(0, nextPos);
    }, duration / scrollSteps);
  }
}