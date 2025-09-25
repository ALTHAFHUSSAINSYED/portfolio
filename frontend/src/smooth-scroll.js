// smooth-scroll.js
// Enhanced smooth scrolling functionality specifically for the contact button

/**
 * Initialize smooth scrolling functionality for the contact button in the header.
 * This provides an enhanced scrolling experience with better positioning and easing.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Initialize after a slight delay to ensure all elements are fully loaded
  setTimeout(() => initContactButtonScroll(), 200);
});

/**
 * Initialize the contact button scroll functionality
 */
function initContactButtonScroll() {
  // Select both desktop and mobile contact buttons
  const contactButtons = document.querySelectorAll('#contact-nav-button, #contact-nav-button-mobile');
  
  // Select the target section
  const contactSection = document.getElementById('contact');
  
  if (contactButtons.length > 0 && contactSection) {
    // Add event listeners to all contact buttons
    contactButtons.forEach(button => {
      button.addEventListener('click', handleContactButtonClick);
    });
    
    console.log(`Smooth scroll handlers initialized for ${contactButtons.length} contact buttons`);
  } else {
    console.warn('Contact buttons or section not found in the DOM. Will retry in 500ms.');
    // Retry after a delay in case elements aren't loaded yet
    setTimeout(() => initContactButtonScroll(), 500);
  }
}

/**
 * Handle the contact button click event
 * @param {Event} e - The click event
 */
function handleContactButtonClick(e) {
  // Prevent default behavior
  e.preventDefault();
  
  const contactSection = document.getElementById('contact');
  
  if (!contactSection) {
    console.error('Contact section not found');
    return;
  }
  
  // Get the target section's position, accounting for the fixed header
  const headerHeight = document.querySelector('header').offsetHeight;
  // Add a small offset for better visual positioning
  const offset = 20;
  const targetPosition = contactSection.getBoundingClientRect().top + window.pageYOffset - headerHeight + offset;
  
  // Perform enhanced smooth scrolling
  smoothScrollTo(targetPosition, 800);
}

/**
 * Custom smooth scroll implementation with easing
 * @param {number} targetPosition - Target scroll position
 * @param {number} duration - Animation duration in milliseconds
 */
function smoothScrollTo(targetPosition, duration) {
  const startPosition = window.pageYOffset;
  const distance = targetPosition - startPosition;
  let startTime = null;
  
  function easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
  }
  
  function animation(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const nextPosition = easeInOutQuad(timeElapsed, startPosition, distance, duration);
    
    window.scrollTo(0, nextPosition);
    
    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  }
  
  // Fall back to standard scrollTo if requestAnimationFrame is not supported
  if ('requestAnimationFrame' in window) {
    requestAnimationFrame(animation);
  } else {
    window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
  }
}