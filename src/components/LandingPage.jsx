import React from "react";
import NavBar from "./NavBar.jsx";

const LandingPage = () => {
  return (
    <div style={{ position: "relative", overflow: "hidden" }}>
      {/* Full-Page Gradient Background */}
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          filter: "blur(20px)",
          background:
            "linear-gradient(143.6deg, rgba(192,132,252,0) 20.79%, rgba(232,121,249,0.26) 40.92%, rgba(204,171,238,0) 70.35%)",
          zIndex: -1,
        }}
      ></div>

      {/* Full Width NavBar. Refixed in app.ks where I removed the div class */}
      <div className="w-100">
        <NavBar />
      </div>

      {/* Main Content Area */}
      <div className="container-fluid px-0">
        {/* Hero / Main Section */}
        <section className="my-5">
          <div className="row align-items-center mx-0">
            {/* Left Column: Text & Buttons */}
            <div className="col-md-6 p-5">
              <h1 className="display-4 fw-bold">
                Catch a ride with a fellow student!
              </h1>
              <p>
                Share your ride, split the cost, and make a new friend on the way
              </p>
              <div className="d-flex gap-2">
                {/* <a href="javascript:void(0)" className="btn btn-dark"> */}
                  Get started by signing up or loggin in above
                {/* </a> */}
              </div>
            </div>
            {/* Right Column: Image with padding */}
            <div className="col-md-6 d-none d-md-block">
              <img
                src="/landingpage.png"
                className="img-fluid p-3"
                alt="Landing"
              />
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-5">
          <h2 className="text-center mb-5">How It Works</h2>
          <div className="row mb-5 px-5">
            {/* For Drivers Card */}
            <div className="col-md-6 mb-4">
              <div
                className="card h-100"
                style={{ backgroundColor: "rgba(255, 255, 255, 0.8)" }}
              >
                <div className="card-body">
                  <h3 className="card-title d-flex align-items-center mb-3">
                    For Drivers
                  </h3>
                  <ol className="list-unstyled">
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-success text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        1
                      </span>
                      <span>
                        Post your journey with your route, date, time, and available
                        seats
                      </span>
                    </li>
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-success text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        2
                      </span>
                      <span>Receive requests from riders along your route</span>
                    </li>
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-success text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        3
                      </span>
                      <span>Accept or decline requests based on the detour time</span>
                    </li>
                    <li className="d-flex align-items-start">
                      <span
                        className="bg-success text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        4
                      </span>
                      <span>Contact your rider and share the journey</span>
                    </li>
                  </ol>
                </div>
              </div>
            </div>

            {/* For Riders Card */}
            <div className="col-md-6 mb-4">
              <div
                className="card h-100"
                style={{ backgroundColor: "rgba(255, 255, 255, 0.8)" }}
              >
                <div className="card-body">
                  <h3 className="card-title d-flex align-items-center mb-3">
                    For Riders
                  </h3>
                  <ol className="list-unstyled">
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        1
                      </span>
                      <span>Enter your pickup and dropoff locations</span>
                    </li>
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        2
                      </span>
                      <span>Browse journeys that match your route</span>
                    </li>
                    <li className="d-flex align-items-start mb-3">
                      <span
                        className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        3
                      </span>
                      <span>Send ride requests to drivers</span>
                    </li>
                    <li className="d-flex align-items-start">
                      <span
                        className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                        style={{ width: "30px", height: "30px" }}
                      >
                        4
                      </span>
                      <span>
                        Once accepted, contact your driver and share the journey
                      </span>
                    </li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default LandingPage;
