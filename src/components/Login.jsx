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
        const response = await fetch('https://catcharide.sarvesh.me/api/checkUser', {
            method: 'POST',
            mode: 'no-cors',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token }),
        });
        
        console.log('Token:', token);
        console.log('Response json: ', response.json);
        console.log('Response body: ', response.body);

        const data = await response.json();
        console.log('Backend response:', data);
        
        // Redirect based on the backend response.
        if (data.exists) {
            navigate('/homepage');
            console.log('Data exists: navigating to homepage');
        } else {
            navigate('/register');
            console.log('Data does notexists: navigating to register page');
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
  console.log("TEST TO MAKE SURE UPDATEDS HERE");
  
  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <Login />
    </GoogleOAuthProvider>
  );
};

export default App;
