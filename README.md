# Smile Classifier

A web-based application for detecting smiles in facial images using a custom-trained convolutional neural network (CNN). The project allows users to upload images, classify them as "smiling" or "not smiling," and view a history of classifications.

## Features
- **Home Page:** Overview of the training process and methodology used to develop the smile classifier.
- **Classify Page:** Upload an image, convert it to the appropriate format if necessary, and classify it in real-time.
- **History Page:** View a table of previous classifications with image paths, predicted class, and timestamps.

## Tech Stack
- **Model Training:** TensorFlow (CNN) for smile detection.
- **Web Framework:** FastAPI for application development.
- **Database:** MySQL for storing classification history.
- **Containerization:** Docker for deploying the project and database in a unified network.
- **Other Tools:** Scikit-learn, SQLAlchemy for ORM, and image processing utilities.

## Deployment
The project is fully containerized using Docker and accessible over a mapped port, ensuring smooth deployment and scalability.

Explore the full code and documentation in this repository. 🚀
