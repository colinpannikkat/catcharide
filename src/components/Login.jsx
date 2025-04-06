import React from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();

  const handleSuccess = async (credentialResponse) => {
    console.log('Login Success:', credentialResponse);
    const token = credentialResponse.credential;

    try {
      // Send token to your Flask backend for verification and user check.
      const response = await fetch('http://localhost:8000/api/checkUser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      
      const data = await response.json();
      console.log('Backend response:', data);
      
      // Redirect based on the backend response.
      if (data.exists) {
        navigate('/homepage');
      } else {
        navigate('/register');
      }
    } catch (error) {
      console.error('Error during user check:', error);
    }
  };

  const handleError = () => {
    console.error('Login Failed');
    // Optionally render some error UI or set state.
  };

  return (
    <div
      className="container d-flex justify-content-center align-items-center"
      style={{ height: '100vh' }}
    >
      <div className="card p-4 shadow">
        <h2 className="text-center mb-4">Login</h2>
        <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
      </div>
    </div>
  );
};

const App = () => {
  console.log("BALALSDMALKSDMASLKDJASLDKJASLKDJASLKDJASLKDJALSDJASLKDJLKASJDALKSJDLAKSJDALSKDJSAKJDKSAD");
  
  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <Login />
    </GoogleOAuthProvider>
  );
};

export default App;
