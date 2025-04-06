import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.css';


// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React testing
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;


import LandingPage from './landingpage.js';
function App() {
  return (
    <div>
      <LandingPage />
    </div>
  );
}

export default App;





// import React from 'react';
// import {APIProvider, Map} from '@vis.gl/react-google-maps';

// const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY

// console.log(GOOGLE_MAPS_API_KEY)
// console.log(process.env)

// const App = () => (
//   <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
//     <Map
//       style={{width: '100vw', height: '100vh'}}
//       defaultCenter={{lat: 22.54992, lng: 0}}
//       defaultZoom={3}
//       gestureHandling={'greedy'}
//       disableDefaultUI={true}
//     />
//   </APIProvider>
// );

// export default App;