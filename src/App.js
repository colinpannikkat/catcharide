import "./App.css";
import "bootstrap/dist/css/bootstrap.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Other pages an components 
import Signup from "./components/Signup.jsx";
import Login from "./components/Login.jsx";
import LandingPage from "./components/LandingPage.jsx";

function App() {
  return (
    <BrowserRouter>
      <div >
        <Routes>
          {/* Landing page route */}
          <Route path="/" element={<LandingPage />} />
          {/* Signup page route */}
          <Route path="/signup" element={<Signup />} />
          {/* Login page route */}
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </BrowserRouter>
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
