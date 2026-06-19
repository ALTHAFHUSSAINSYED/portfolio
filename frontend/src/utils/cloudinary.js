// Cloudinary Image Optimization Utility
// Provides helper functions for optimized image delivery with automatic format and quality selection

const CLOUDINARY_CLOUD_NAME = 'dtzaicj6s';
const CLOUDINARY_BASE_URL = `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}`;

/**
 * Generate optimized Cloudinary image URL with transformations
 * @param {string} publicId - Cloudinary public ID of the image
 * @param {object} options - Transformation options
 * @param {number} options.width - Target width (responsive)
 * @param {number} options.height - Target height
 * @param {string} options.crop - Crop mode (default: 'fill')
 * @param {string} options.gravity - Focus area (default: 'auto')
 * @param {number} options.quality - Quality (default: 'auto')
 * @param {string} options.format - Format (default: 'auto')
 * @returns {string} Optimized Cloudinary URL
 */
export const getOptimizedImageUrl = (publicId, options = {}) => {
  const {
    width = 'auto',
    height,
    crop = 'fill',
    gravity = 'auto',
    quality = 'auto',
    format = 'auto',
  } = options;

  let transformations = [
    `f_${format}`, // Automatic format selection (WebP, AVIF, etc.)
    `q_${quality}`, // Automatic quality optimization
  ];

  if (width !== 'auto') {
    transformations.push(`w_${width}`);
  }

  if (height) {
    transformations.push(`h_${height}`);
  }

  if (crop) {
    transformations.push(`c_${crop}`);
  }

  if (gravity) {
    transformations.push(`g_${gravity}`);
  }

  const transformationString = transformations.join(',');

  return `${CLOUDINARY_BASE_URL}/image/upload/${transformationString}/${publicId}`;
};

/**
 * Generate optimized Cloudinary video URL with transformations
 * @param {string} publicId - Cloudinary public ID of the video
 * @param {object} options - Transformation options
 * @returns {string} Optimized Cloudinary video URL
 */
export const getOptimizedVideoUrl = (publicId, options = {}) => {
  const {
    quality = 'auto',
    format = 'auto',
  } = options;

  const transformations = [
    `f_${format}`, // Automatic format selection
    `q_${quality}`, // Automatic quality
  ].join(',');

  return `${CLOUDINARY_BASE_URL}/video/upload/${transformations}/${publicId}`;
};

/**
 * Generate responsive image srcset for Cloudinary images
 * Useful for <img srcset=""> or <picture> elements
 * @param {string} publicId - Cloudinary public ID
 * @param {array} widths - Array of widths (e.g., [320, 640, 1024, 1920])
 * @returns {string} srcset string
 */
export const getResponsiveSrcSet = (publicId, widths = [320, 640, 1024, 1920]) => {
  return widths
    .map(width => {
      const url = getOptimizedImageUrl(publicId, { width, quality: 'auto', format: 'auto' });
      return `${url} ${width}w`;
    })
    .join(', ');
};

export default {
  getOptimizedImageUrl,
  getOptimizedVideoUrl,
  getResponsiveSrcSet,
};
