# Eye Disease API

This project is an API for managing patient data and generating medical reports for eye diseases. It includes functionalities for user sign-in, patient registration, disease prediction, and generating PDF reports.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/eye_disease_api.git
    cd eye_disease_api
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Start the Flask application:
    ```sh
    flask run
    ```

2. The API will be available at `http://127.0.0.1:5000/`.

## API Endpoints

### User Sign-In
- **Endpoint:** `/user-signin`
- **Method:** `POST`
- **Description:** Registers a new user.

### User Login
- **Endpoint:** `/user-login`
- **Method:** `POST`
- **Description:** Logs in an existing user.

### Register Patient
- **Endpoint:** `/register-patient`
- **Method:** `POST`
- **Description:** Registers a new patient.

### Generate Report
- **Endpoint:** `/report`
- **Method:** `GET`
- **Description:** Generates a PDF report for a patient.

### Predict Disease
- **Endpoint:** `/predict`
- **Method:** `POST`
- **Description:** Predicts the eye disease from an uploaded image.

### Prediction History
- **Endpoint:** `/prediction-history`
- **Method:** `GET`
- **Description:** Retrieves the prediction history for a patient.

### Nearest Eye Specialists
- **Endpoint:** `/nearest_eye_specialists`
- **Method:** `GET`
- **Description:** Retrieves the nearest eye specialists based on the user's location.

