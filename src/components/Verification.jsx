import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';

async function getUser(token) {
    // Send token to your Flask backend for verification and user check.
    const response = await fetch('http://localhost:8000/api/getUser', {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ token }),
    });

    return response.body.json()
}

const VerificationPage = () => {
    const navigate = useNavigate()
    const handleSubmit = async (event) => {
        event.preventDefault();

        const idFile = document.querySelector("#idUpload").files[0];
        const imageFile = document.querySelector("#imageUpload").files[0];

        if (idFile) {
            const idReader = new FileReader();
            idReader.onload = () => {
            const idBase64 = btoa(idReader.result);
            formData.append("id_base64", idBase64);
            };
            idReader.readAsDataURL(idFile);
        }

        if (imageFile) {
            const imageReader = new FileReader();
            imageReader.onload = () => {
            const imageBase64 = btoa(imageReader.result);
            formData.append("image_base64", imageBase64);
            };
            imageReader.readAsDataURL(imageFile);
        }

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
                navigate('/login')
                return;
            }
            try {
                const res = await getUser()
                if (res.exists) {
                    formData.append("first_name", res.body.first_name);
                    formData.append("last_name", res.body.last_name);
                    formData.append("user_db_id", res.body.id)
                } else {
                    alert("User verification token invalid. Please log in again.")
                    navigate('/login')
                    return;
                }

            } catch (error) {
                console.error('Error during user check:', error);
            }
            const response = await fetch("http://localhost:8000/api/verify", {
                method: "POST",
                mode: "no-cors",
                headers: {
                    Authorization: `Bearer ${authToken}`,
                },
                body: formData, // Content-Type will be set automatically
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
                        onChange={(e) => {
                            const file = e.target.files[0];
                            if (file && file.size > 4 * 1024 * 1024) {
                                alert("ID file size exceeds 4MB. Please upload a smaller file.");
                                e.target.value = null;
                            }
                        }}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="imageUpload" className="form-label">Upload Image</label>
                    <input
                        type="file"
                        id="imageUpload"
                        className="form-control"
                        accept="image/*"
                        onChange={(e) => {
                            const file = e.target.files[0];
                            if (file && file.size > 4 * 1024 * 1024) {
                                alert("Image file size exceeds 4MB. Please upload a smaller file.");
                                e.target.value = null;
                            }
                        }}
                    />
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
            </form>
        </div>
    );
};

export default VerificationPage;