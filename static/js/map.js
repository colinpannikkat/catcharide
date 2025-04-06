// Map initialization and management

let map;
let directionsService;
let directionsRenderer;
let autocompleteOrigin;
let autocompleteDestination;

// Initialize the map with default center and zoom
function initMap() {
  // Check if Google Maps API is loaded
  if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
    console.error('Google Maps API not loaded');
    return;
  }

  // Create a map centered on Oregon
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 44.5, lng: -123.0 }, // Approximate center of Oregon
    zoom: 7,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_RIGHT
    },
    fullscreenControl: true,
    streetViewControl: true,
    zoomControl: true
  });

  // Initialize the DirectionsService and DirectionsRenderer
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map: map,
    suppressMarkers: false,
    polylineOptions: {
      strokeColor: '#D73F09', // OSU Orange
      strokeWeight: 5,
      strokeOpacity: 0.7
    }
  });

  // Set up autocomplete for location inputs if they exist
  setupAutocomplete();
}

// Setup Google Places Autocomplete for location inputs
function setupAutocomplete() {
  const originInput = document.getElementById('origin');
  const destinationInput = document.getElementById('destination');
  
  if (originInput && destinationInput) {
    // Options for Autocomplete
    const options = {
      componentRestrictions: { country: 'us' },
      fields: ['place_id', 'geometry', 'name', 'formatted_address']
    };
    
    // Create Autocomplete objects
    autocompleteOrigin = new google.maps.places.Autocomplete(originInput, options);
    autocompleteDestination = new google.maps.places.Autocomplete(destinationInput, options);
    
    // Add event listeners
    autocompleteOrigin.addListener('place_changed', function() {
      const place = autocompleteOrigin.getPlace();
      if (place.place_id) {
        document.getElementById('origin-place-id').value = place.place_id;
        document.getElementById('origin-display').value = place.name + ', ' + place.formatted_address;
      }
    });
    
    autocompleteDestination.addListener('place_changed', function() {
      const place = autocompleteDestination.getPlace();
      if (place.place_id) {
        document.getElementById('destination-place-id').value = place.place_id;
        document.getElementById('destination-display').value = place.name + ', ' + place.formatted_address;
      }
    });
  }
}

// Display a route on the map using Google Directions Service
function displayRoute(origin, destination) {
  const request = {
    origin: { placeId: origin },
    destination: { placeId: destination },
    travelMode: google.maps.TravelMode.DRIVING,
    optimizeWaypoints: true
  };
  
  directionsService.route(request, function(response, status) {
    if (status === google.maps.DirectionsStatus.OK) {
      directionsRenderer.setDirections(response);
      
      // Display route information
      const route = response.routes[0];
      const distance = route.legs[0].distance.text;
      const duration = route.legs[0].duration.text;
      
      const routeInfoDiv = document.getElementById('route-info');
      if (routeInfoDiv) {
        routeInfoDiv.innerHTML = `
          <div class="d-flex justify-content-between mb-3">
            <div>
              <strong>Distance:</strong> ${distance}
            </div>
            <div>
              <strong>Estimated Time:</strong> ${duration}
            </div>
          </div>
        `;
      }
    } else {
      console.error('Directions request failed due to ' + status);
      alert('Unable to display route. Please try again.');
    }
  });
}

// Display a route using an encoded polyline
function displayPolyline(encodedPolyline) {
  if (!map) {
    console.error('Map not initialized');
    return;
  }
  
  // Clear previous routes
  directionsRenderer.setMap(null);
  
  // Decode the polyline
  const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline);
  
  // Create a new Polyline
  const polyline = new google.maps.Polyline({
    path: decodedPath,
    strokeColor: '#D73F09', // OSU Orange
    strokeWeight: 5,
    strokeOpacity: 0.7
  });
  
  // Set the polyline on the map
  polyline.setMap(map);
  
  // Fit the map to the polyline bounds
  const bounds = new google.maps.LatLngBounds();
  decodedPath.forEach(function(point) {
    bounds.extend(point);
  });
  map.fitBounds(bounds);
}

// Format duration in seconds to a human-readable string
function formatDuration(seconds) {
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

// Format distance in meters to a human-readable string
function formatDistance(meters) {
  const miles = (meters / 1609.34).toFixed(1);
  return miles + ' miles';
}

// Initialize map when the page loads
document.addEventListener('DOMContentLoaded', function() {
  // Check if the map container exists on the page
  if (document.getElementById('map')) {
    // Load Google Maps script dynamically if it hasn't been loaded yet
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places,geometry&callback=initMap`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    } else {
      // If Google Maps is already loaded, initialize the map directly
      initMap();
    }
  }
});
