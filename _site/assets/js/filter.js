// assets/js/filter.js
document.addEventListener('DOMContentLoaded', function () {
  const filterContainer = document.querySelector('#filter-container');
  const projectGrid = document.querySelector('#project-grid');
  
  if (!filterContainer) return; // Exit if there's no filter container on the page

  const filterButtons = filterContainer.querySelectorAll('.filter-btn');
  const projectCards = projectGrid.querySelectorAll('.card');

  // We need to target the .card-link (the wrapper) because it participates in the CSS grid.
  const projectCardLinks = projectGrid.querySelectorAll('.card-link');

  filterButtons.forEach(button => {
    button.addEventListener('click', function () {
      // Handle active button state
      filterButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');

      const filterValue = this.getAttribute('data-filter');

      // Loop through all project card wrappers
      projectCardLinks.forEach(link => {
        if (filterValue === 'all' || link.getAttribute('data-category') === filterValue) {
          link.style.display = 'block'; // Show wrapper
        } else {
          link.style.display = 'none'; // Hide wrapper entirely
        }
      });
    });
  });
});

// --- Live Counter Animation ---
document.addEventListener('DOMContentLoaded', function () {
  const counters = document.querySelectorAll('.counter');
  
  const animateCounter = (counter) => {
    const target = +counter.getAttribute('data-count');
    const duration = 2000; // 2 seconds
    const increment = target / (duration / 16); // Calculate increment for smooth animation

    let current = 0;

    const updateCounter = () => {
      current += increment;
      if (current < target) {
        counter.innerText = Math.ceil(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.innerText = target; // Ensure it ends on the exact number
      }
    };
    
    updateCounter();
  };

  // Use Intersection Observer to trigger animation only when visible
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target); // Animate only once
      }
    });
  }, { threshold: 0.5 }); // Trigger when 50% of the element is visible

  counters.forEach(counter => {
    observer.observe(counter);
  });
});
// assets/js/filter.js (add to the end)

// --- Skills Modal Logic ---
document.addEventListener('DOMContentLoaded', function () {
  const trigger = document.getElementById('skills-stats-trigger');
  const modal = document.getElementById('skills-modal');
  
  if (!trigger || !modal) return; // Exit if elements don't exist
  
  const closeButton = modal.querySelector('.close-button');

  const openModal = () => modal.classList.add('modal-open');
  const closeModal = () => modal.classList.remove('modal-open');

  // Open the modal
  trigger.addEventListener('click', openModal);

  // Close the modal via the 'X' button
  closeButton.addEventListener('click', closeModal);

  // Close the modal by clicking the background overlay
  modal.addEventListener('click', function(event) {
    if (event.target === modal) {
      closeModal();
    }
  });

  // Close the modal by pressing the 'Escape' key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && modal.classList.contains('modal-open')) {
      closeModal();
    }
  });
});