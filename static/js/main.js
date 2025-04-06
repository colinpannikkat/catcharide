// Main JavaScript file for CatchARide

// Global variable for API key - this will be set from the template
let GOOGLE_MAPS_API_KEY;

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Handle flash message dismissal
  setupFlashMessageDismissal();

  // Handle date formatting
  formatDates();

  // Setup forms if they exist
  setupForms();
});

// Format all dates on the page
function formatDates() {
  const dateElements = document.querySelectorAll('.format-date');
  
  dateElements.forEach(element => {
    const dateStr = element.textContent.trim();
    if (dateStr) {
      try {
        const date = new Date(dateStr);
        element.textContent = formatDate(date);
      } catch (e) {
        console.error('Error formatting date:', e);
      }
    }
  });
  
  const dateTimeElements = document.querySelectorAll('.format-datetime');
  
  dateTimeElements.forEach(element => {
    const dateStr = element.textContent.trim();
    if (dateStr) {
      try {
        const date = new Date(dateStr);
        element.textContent = formatDateTime(date);
      } catch (e) {
        console.error('Error formatting datetime:', e);
      }
    }
  });
}

// Format a date object to a readable string
function formatDate(date) {
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

// Format a date object with time to a readable string
function formatDateTime(date) {
  const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true };
  
  const dateStr = date.toLocaleDateString('en-US', dateOptions);
  const timeStr = date.toLocaleTimeString('en-US', timeOptions);
  
  return `${dateStr} at ${timeStr}`;
}

// Setup flash message dismissal
function setupFlashMessageDismissal() {
  const flashMessages = document.querySelectorAll('.alert');
  
  flashMessages.forEach(message => {
    const closeButton = message.querySelector('.btn-close');
    if (closeButton) {
      closeButton.addEventListener('click', function() {
        message.remove();
      });
      
      // Auto-dismiss after 5 seconds if it's not an error
      if (!message.classList.contains('alert-danger')) {
        setTimeout(() => {
          message.classList.add('fade');
          setTimeout(() => {
            message.remove();
          }, 500);
        }, 5000);
      }
    }
  });
}

// Setup forms with validation and other features
function setupForms() {
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    // Handle form validation
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      form.classList.add('was-validated');
    }, false);
    
    // Handle place search if this is a form with location inputs
    setupPlaceSearch(form);
  });
}

// Setup place search functionality for origin and destination fields
function setupPlaceSearch(form) {
  const originInput = form.querySelector('#origin');
  const destinationInput = form.querySelector('#destination');
  
  if (originInput && destinationInput) {
    // If the placeholders are not set, set them
    if (!originInput.placeholder) {
      originInput.placeholder = 'Enter origin location';
    }
    if (!destinationInput.placeholder) {
      destinationInput.placeholder = 'Enter destination location';
    }
    
    // Make sure the hidden fields for place IDs exist
    if (!form.querySelector('#origin-place-id')) {
      const originPlaceIdInput = document.createElement('input');
      originPlaceIdInput.type = 'hidden';
      originPlaceIdInput.id = 'origin-place-id';
      originPlaceIdInput.name = 'origin';
      form.appendChild(originPlaceIdInput);
    }
    
    if (!form.querySelector('#destination-place-id')) {
      const destPlaceIdInput = document.createElement('input');
      destPlaceIdInput.type = 'hidden';
      destPlaceIdInput.id = 'destination-place-id';
      destPlaceIdInput.name = 'destination';
      form.appendChild(destPlaceIdInput);
    }
    
    // Make sure the hidden fields for display values exist
    if (!form.querySelector('#origin-display')) {
      const originDisplayInput = document.createElement('input');
      originDisplayInput.type = 'hidden';
      originDisplayInput.id = 'origin-display';
      originDisplayInput.name = 'origin_display';
      form.appendChild(originDisplayInput);
    }
    
    if (!form.querySelector('#destination-display')) {
      const destDisplayInput = document.createElement('input');
      destDisplayInput.type = 'hidden';
      destDisplayInput.id = 'destination-display';
      destDisplayInput.name = 'destination_display';
      form.appendChild(destDisplayInput);
    }
  }
}

// Utility function to convert seconds to hours and minutes
function secondsToHoursMinutes(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  let result = '';
  if (hours > 0) {
    result += hours + ' hour' + (hours > 1 ? 's' : '') + ' ';
  }
  if (minutes > 0 || hours === 0) {
    result += minutes + ' minute' + (minutes > 1 ? 's' : '');
  }
  
  return result.trim();
}

// Utility function to convert meters to miles
function metersToMiles(meters) {
  return (meters / 1609.34).toFixed(1) + ' miles';
}

// Utility function to handle confirmation dialogs
function confirmAction(message, callback) {
  if (confirm(message)) {
    callback();
  }
}
