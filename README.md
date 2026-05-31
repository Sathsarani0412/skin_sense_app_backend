# Skin Sense Backend

## Overview

Skin Sense Backend is a Flask-based server application that powers the Skin Sense mobile application. The backend handles image processing, machine learning predictions, user management, recommendation generation, and skin progress tracking using TensorFlow and SQLite.

## Features

### REST API Services

* User Authentication APIs
* Image Upload APIs
* Skin Analysis APIs
* Progress Tracking APIs
* Recommendation APIs

### AI-Based Skin Analysis

The backend processes facial images and predicts the severity of:

* Dark Spots
* Wrinkles
* Blackheads
* Whiteheads


### Prediction Processing

The system returns:

* Prediction percentages
* Dominant skin condition
* Recommendation data
* Historical analysis records

### Progress Monitoring

The backend stores prediction history and allows users to:

* Compare previous analyses
* Track skin condition changes
* Generate progress reports

## Machine Learning Dataset

The model was trained using the Kaggle dataset:

Facial Skin Condition Dataset for AI (Acne, Pigmentation, Pores, Wrinkles)

Dataset Categories:

* Dark Spots
* Inflammatory Acne
* Non-Inflammatory Acne (Blackheads)
* Non-Inflammatory Acne (Whiteheads)
* Pigmentation
* Pores
* Redness
* Wrinkles

The dataset was designed for facial skin condition classification and AI-powered dermatological analysis.

## Model Performance

* Training Accuracy: High Performance
* Validation Accuracy: High Performance
* Test Accuracy: 93%

## Technologies Used

* Python
* Flask
* TensorFlow
* Keras
* OpenCV
* NumPy
* SQLite

## System Architecture

Flutter Mobile Application
↓
Flask REST API
↓
Image Preprocessing
↓
TensorFlow Prediction Model
↓
Skin Condition Classification
↓
Recommendation Engine
↓
SQLite Database
↓
Response to Client Application

## Future Improvements

* Cloud Database Support
* Advanced Recommendation Engine
* Multi-Condition Detection
* Dermatologist Integration
* Real-Time Skin Monitoring
* AI-Based Product Recommendations
