// smooth-scroll.js
// A dedicated script to implement smooth scrolling functionality for the contact button

/**
 * Initialize smooth scrolling functionality for the contact button in the header.
 * This enhances the basic CSS 'scroll-behavior: smooth' with a more controlled animation.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Select the contact button by its ID
  const contactButton = document.getElementById('contact-nav-button');
  
  // Select the target section
  const contactSection = document.getElementById('contact');
  
  if (contactButton && contactSection) {
    // Add click event listener to the contact button
    contactButton.addEventListener('click', function(e) {
      // Prevent default behavior if it's an anchor tag
      e.preventDefault();
      
      // Get the target section's position, accounting for the fixed header
      const headerHeight = document.querySelector('header').offsetHeight;
      const targetPosition = contactSection.getBoundingClientRect().top + window.pageYOffset - headerHeight;
      
      // Perform smooth scrolling with improved behavior
      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
    });
    
    console.log('Smooth scroll handler initialized for contact button');
  } else {
    console.warn('Contact button or section not found in the DOM');
  }
});