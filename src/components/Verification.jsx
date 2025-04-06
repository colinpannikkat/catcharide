import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

async function getUser(token) {
    // Send token to your Flask backend for verification and user check.
    const response = await fetch('https://catcharide.sarvesh.me/api/getUser', {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ token }),
    });

    return body.json()
}

const VerificationPage = () => {
    const handleSubmit = async (event) => {
        event.preventDefault();

        const idFile = document.querySelector("#idUpload").files[0];
        const imageFile = document.querySelector("#imageUpload").files[0];

        if (!idFile || !imageFile) {
            alert("Please upload both ID and Image.");
            return;
        }

        const formData = new FormData();
        formData.append("id", idFile);
        formData.append("image", imageFile);

        try {
            const authToken = localStorage.getItem("authToken"); // Retrieve auth token from local storage
            if (!authToken) {
                alert("Authentication token is missing. Please log in again.");
                return;
            }
            try {
                const res = await getUser()
                if (data.exists) {
                    formData.append("first_name", res.body.first_name);
                    formData.append("last_name", res.body.last_name);
                } else {
                    alert("User verification token invalid. Please log in again.")
                }

            } catch (error) {
                console.error('Error during user check:', error);
            }
            const response = await fetch("https://catcharide.sarvesh.me/api/verify", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${authToken}`,
                },
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log("Success:", result);
                alert("Verification successful!");
            } else {
                console.error("Error:", response.statusText);
                alert("Verification failed.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred while submitting the form.");
        }
    };

    return (
        <div className="container mt-5">
            <h2>Verification Page</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="idUpload" className="form-label">Upload ID</label>
                    <input
                        type="file"
                        id="idUpload"
                        className="form-control"
                        accept="image/*"
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="imageUpload" className="form-label">Upload Image</label>
                    <input
                        type="file"
                        id="imageUpload"
                        className="form-control"
                        accept="image/*"
                    />
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
            </form>
        </div>
    );
};

export default VerificationPage;