// Route-specific JavaScript functions for CatchARide

// Load and display route optimizations on search results page
function loadRouteOptimizations(rideOffers) {
  if (!rideOffers || rideOffers.length === 0) {
    return;
  }
  
  // Select the first ride offer for display on the map
  displayRideOfferRoute(rideOffers[0]);
  
  // Add click handlers to all rides to display their routes
  rideOffers.forEach((offer, index) => {
    const rideCard = document.getElementById(`ride-${offer.id}`);
    if (rideCard) {
      rideCard.addEventListener('click', function() {
        displayRideOfferRoute(offer);
        
        // Highlight the selected card
        document.querySelectorAll('.ride-card').forEach(card => {
          card.classList.remove('border-primary');
        });
        rideCard.classList.add('border-primary');
      });
    }
  });
}

// Display a ride offer's route on the map
function displayRideOfferRoute(rideOffer) {
  if (!rideOffer || !rideOffer.polyline) {
    console.error('No polyline data available for this ride offer');
    return;
  }
  
  // Display the polyline on the map
  displayPolyline(rideOffer.polyline);
  
  // Update the route information display
  updateRouteInfo(rideOffer);
}

// Update the route information display with data from the selected ride
function updateRouteInfo(rideOffer) {
  const routeInfoDiv = document.getElementById('route-info');
  if (!routeInfoDiv) {
    return;
  }
  
  // Format the duration and distance
  const duration = secondsToHoursMinutes(rideOffer.total_duration);
  const distance = metersToMiles(rideOffer.total_distance);
  
  // Update the route info display
  routeInfoDiv.innerHTML = `
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Route Information</h5>
        <div class="row">
          <div class="col-md-6">
            <p><strong>Total Duration:</strong> ${duration}</p>
            <p><strong>Total Distance:</strong> ${distance}</p>
          </div>
          <div class="col-md-6">
            <p><strong>Driver:</strong> ${rideOffer.driver_name}</p>
            <p><strong>Available Seats:</strong> ${rideOffer.available_seats}</p>
          </div>
        </div>
        <div class="mt-3">
          <a href="/routes/ride_details/${rideOffer.id}" class="btn btn-primary">View Details</a>
          <a href="/passengers/apply_ride/${rideOffer.id}" class="btn btn-outline-primary">Apply for Ride</a>
        </div>
      </div>
    </div>
  `;
}

// Search for rides with form validation
function searchRides(formId) {
  const form = document.getElementById(formId);
  if (!form) {
    console.error('Search form not found');
    return false;
  }
  
  // Check if origin and destination are set
  const originPlaceId = document.getElementById('origin-place-id').value;
  const destPlaceId = document.getElementById('destination-place-id').value;
  
  if (!originPlaceId || !destPlaceId) {
    alert('Please select valid origin and destination locations from the suggestions.');
    return false;
  }
  
  // Form is valid, submit it
  return true;
}

// Initialize the ride offers display on the search results page
document.addEventListener('DOMContentLoaded', function() {
  const rideOffersData = document.getElementById('ride-offers-data');
  
  if (rideOffersData) {
    try {
      const rideOffers = JSON.parse(rideOffersData.textContent);
      loadRouteOptimizations(rideOffers);
    } catch (e) {
      console.error('Error parsing ride offers data:', e);
    }
  }
  
  // Add event listener to search form
  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', function(event) {
      if (!searchRides('search-form')) {
        event.preventDefault();
      }
    });
  }
});

// Load and display a single ride's route for the ride details page
function loadRideDetails(rideOffer, optimizedData) {
  if (!rideOffer) {
    return;
  }
  
  // If we have optimized data with a polyline, display it
  if (optimizedData && optimizedData.polyline) {
    displayPolyline(optimizedData.polyline);
    
    // Update the optimized route information
    const optimizedInfoDiv = document.getElementById('optimized-route-info');
    if (optimizedInfoDiv) {
      const duration = secondsToHoursMinutes(optimizedData.total_duration);
      const distance = metersToMiles(optimizedData.total_distance);
      
      optimizedInfoDiv.innerHTML = `
        <div class="card mb-4">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Optimized Route (Including Your Trip)</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Total Duration:</strong> ${duration}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Total Distance:</strong> ${distance}</p>
              </div>
            </div>
          </div>
        </div>
      `;
    }
  } else {
    // If no optimized data, display a basic route
    displayRoute(rideOffer.origin, rideOffer.destination);
  }
}

// Initialize the ride details page
document.addEventListener('DOMContentLoaded', function() {
  const rideDetailsData = document.getElementById('ride-details-data');
  const optimizedRouteData = document.getElementById('optimized-route-data');
  
  if (rideDetailsData) {
    try {
      const rideOffer = JSON.parse(rideDetailsData.textContent);
      let optimizedData = null;
      
      if (optimizedRouteData) {
        try {
          optimizedData = JSON.parse(optimizedRouteData.textContent);
        } catch (e) {
          console.error('Error parsing optimized route data:', e);
        }
      }
      
      loadRideDetails(rideOffer, optimizedData);
    } catch (e) {
      console.error('Error parsing ride details data:', e);
    }
  }
});
