import React from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';

async function checkUser(token) {
    // Send token to your Flask backend for verification and user check.
    const response = await fetch('http://localhost:8000/api/checkUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ token }),
    });

    // Store the token in local storage
    localStorage.setItem('authToken', token);
    
    console.log('Token:', token);

    const result = await response.json();
    if (response.ok) {
        return result;
    } else {
        throw new Error(result.message || 'Failed to verify user');
    }
}

const Login = () => {
  const navigate = useNavigate();

  const handleSuccess = async (credentialResponse) => {
    console.log('Login Success:', credentialResponse);
    let token = credentialResponse.credential;

    try {
        const data = await checkUser(token);
        console.log('Backend response:', data);
        
        // Redirect based on the backend response.
        if (data.exists) {
            if (!data.is_verified)
                navigate('/verify');
            else
                navigate('/')
            console.log('Data exists: navigating to verification page');
        } else {
            alert('Login data does not exists: try again');
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
