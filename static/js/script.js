document.addEventListener('DOMContentLoaded', function() {
  // Theme toggle functionality
  const themeToggle = document.getElementById('themeToggle');
  const body = document.body;

  // Check if user has a theme preference stored
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    body.classList.add('dark-theme');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  }

  // Toggle between light and dark theme
  themeToggle.addEventListener('click', function() {
    if (body.classList.contains('dark-theme')) {
      body.classList.remove('dark-theme');
      themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
      localStorage.setItem('theme', 'light');
    } else {
      body.classList.add('dark-theme');
      themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
      localStorage.setItem('theme', 'dark');
    }
  });

  // Mobile sidebar toggle
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.querySelector('.sidebar');

  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(event) {
    if (window.innerWidth <= 768 && 
        !sidebar.contains(event.target) && 
        !menuToggle.contains(event.target) && 
        sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
    }
  });

  // Flash message auto-dismiss
  const flashMessages = document.querySelectorAll('.alert');
  if (flashMessages.length > 0) {
    flashMessages.forEach(message => {
      setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => {
          message.remove();
        }, 500);
      }, 5000);
    });
  }

  // Item quantity validation
  const quantityChange = document.getElementById('quantity_change');
  const adjustmentType = document.getElementById('adjustment_type');

  if (quantityChange && adjustmentType) {
    adjustmentType.addEventListener('change', function() {
      if (this.value === 'OUT') {
        quantityChange.setAttribute('data-original-title', 'Cannot remove more than available quantity');
      } else {
        quantityChange.removeAttribute('data-original-title');
      }
    });
  }

  // Form validation for stock adjustment
  const adjustForm = document.querySelector('form.item-form');
  if (adjustForm) {
    adjustForm.addEventListener('submit', function(event) {
      const itemId = document.getElementById('item_id').value;
      const adjustType = document.getElementById('adjustment_type').value;
      const qtChange = document.getElementById('quantity_change').value;

      if (!itemId || !adjustType || !qtChange || parseInt(qtChange) <= 0) {
        event.preventDefault();
        alert('Please fill in all required fields with valid values.');
      }
    });
  }

  // Enhanced dropdowns with search
  const enhancedSelects = document.querySelectorAll('select#item_id');
  if (enhancedSelects.length > 0) {
    enhancedSelects.forEach(select => {
      // Add search functionality to select elements
      const wrapper = document.createElement('div');
      wrapper.className = 'enhanced-select-wrapper';

      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.className = 'select-search';
      searchInput.placeholder = 'Search items...';

      // Insert the search before the select
      select.parentNode.insertBefore(wrapper, select);
      wrapper.appendChild(searchInput);
      wrapper.appendChild(select);

      // Filter options based on search
      searchInput.addEventListener('input', function() {
        const filter = this.value.toLowerCase();
        const options = select.querySelectorAll('option');

        options.forEach(option => {
          if (option.value === '') return; // Skip placeholder option

          const text = option.textContent.toLowerCase();
          if (text.indexOf(filter) > -1) {
            option.style.display = '';
          } else {
            option.style.display = 'none';
          }
        });
      });
    });
  }

  // Table row highlighting on hover
  const tableRows = document.querySelectorAll('table tbody tr');
  tableRows.forEach(row => {
    row.addEventListener('mouseover', function() {
      this.classList.add('highlight');
    });

    row.addEventListener('mouseout', function() {
      this.classList.remove('highlight');
    });
  });

  // Confirm delete action
  const deleteButtons = document.querySelectorAll('.delete-btn');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        event.preventDefault();
      }
    });
  });
});