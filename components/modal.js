/**
 * Image Modal Lightbox
 * Lightweight vanilla JS modal for gallery image enlargement
 * Features: ESC close, overlay click, fade animations, ARIA labels
 */

(function() {
  let modalOpen = false;

  // Create modal HTML structure
  const createModal = () => {
    const modal = document.createElement('div');
    modal.id = 'image-modal';
    modal.className = 'modal-backdrop';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'Image viewer');
    modal.innerHTML = `
      <div class="modal-container">
        <button class="modal-close" aria-label="Close image viewer">
          <span aria-hidden="true">&times;</span>
        </button>
        <img class="modal-image" alt="" />
        <div class="modal-caption"></div>
      </div>
    `;
    return modal;
  };

  // Initialize modal if not exists
  const getModal = () => {
    let modal = document.getElementById('image-modal');
    if (!modal) {
      modal = createModal();
      document.body.appendChild(modal);
      attachEventListeners(modal);
    }
    return modal;
  };

  // Attach event listeners
  const attachEventListeners = (modal) => {
    const backdrop = modal;
    const closeBtn = modal.querySelector('.modal-close');
    const container = modal.querySelector('.modal-container');

    // Close on ESC key
    const handleEscape = (e) => {
      if (e.key === 'Escape') closeModal();
    };

    // Close on backdrop click (not container click)
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeModal();
    });

    // Close on close button
    closeBtn.addEventListener('click', closeModal);

    // Prevent container click from closing
    container.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    // Attach ESC listener when modal opens
    modal._escListener = handleEscape;
  };

  // Open modal with image
  window.openModal = function(imageSrc, imageAlt, imageTitle) {
    const modal = getModal();
    const img = modal.querySelector('.modal-image');
    const caption = modal.querySelector('.modal-caption');

    img.src = imageSrc;
    img.alt = imageAlt || 'Image';
    caption.textContent = imageTitle || '';

    // Set aria-label
    modal.setAttribute('aria-label', `Image viewer: ${imageAlt || 'Image'}`);

    // Show modal
    modal.classList.add('modal-open');
    document.body.style.overflow = 'hidden';
    document.body.setAttribute('aria-hidden', 'true');

    // Add ESC listener
    document.addEventListener('keydown', modal._escListener);
    modalOpen = true;
  };

  // Close modal
  window.closeModal = function() {
    const modal = getModal();

    // Hide modal
    modal.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.setAttribute('aria-hidden', 'false');

    // Remove ESC listener
    if (modal._escListener) {
      document.removeEventListener('keydown', modal._escListener);
    }
    modalOpen = false;
  };
})();
