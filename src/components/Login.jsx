import React from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import 'bootstrap/dist/css/bootstrap.min.css';



const Login = () => {
  const handleSuccess = (credentialResponse) => {
    console.log('Login Success:', credentialResponse);
    // Handle the credential response (e.g., send the token to your server)
  };

  const handleError = () => {
    console.error('Login Failed');
    <div>
        <h1>Login Failed</h1>
    </div>
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
