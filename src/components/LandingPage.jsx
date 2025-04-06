import React from "react";
import NavBar from "./NavBar.jsx";

const LandingPage = () => {
  return (
    <div style={{ position: "relative" }}>
      {/* Background Blur Effect */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "580px",
          filter: "blur(20px)",
          background:
            "linear-gradient(143.6deg, rgba(192,132,252,0) 20.79%, rgba(232,121,249,0.26) 40.92%, rgba(204,171,238,0) 70.35%)",
          zIndex: -1,
        }}
      ></div>

      {/*use the Navbar from NavBar.jsx and remove it from the app.js file */}
      <NavBar />

      {/* Main Section */}
      <section className="container my-5">
        <div className="row align-items-center">
          {/* Left Column: Text & Buttons */}
          <div className="col-md-6">
            <h1 className="display-4 fw-bold">
              Catch a ride with a 
              fellow student!
            </h1>
            <p>
              Share your ride, split the cost, and make a new friend on the way
            </p>
            <div className="d-flex gap-2">
              <a href="javascript:void(0)" className="btn btn-dark">
                Get started
              </a>
            </div>
          </div>
          {/* Right Column: Image */}
          <div className="col-md-6 d-none d-md-block">
            {/* <img
              src="https://raw.githubusercontent.com/sidiDev/remote-assets/c86a7ae02ac188442548f510b5393c04140515d7/undraw_progressive_app_m-9-ms_oftfv5.svg"
              alt="Landing Illustration"
              className="img-fluid"
            /> */}
            <img
            src="/landingpage.png"  
            className="img-fluid"
          />
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;