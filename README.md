# PDF Image Extraction and Classification Microservice

## Overview
This microservice extracts and classifies images from PDF files. It is designed to work in a multithreaded environment for high performance and scalability.

## Features
- Listens to a RabbitMQ queue for notifications about new PDF files to process.
- Downloads the PDF files from an S3-compatible file storage.
- Extracts images from the PDFs using PyMuPDF.
  - Experimental support for image extraction using Tesseract is also included.
- Classifies the extracted images using a custom TensorFlow-based CNN model (previously used CLIP-based classifier).
- Uploads the classified images to a separate S3 bucket for images.
- Stores metadata about the extracted images and their associated PDFs in a MongoDB database.
- Sends a new message to a RabbitMQ queue containing the list of uploaded image locations in S3.

## Technologies
- **FastAPI** — for exposing internal APIs and health checks.
- **PyMuPDF** — for efficient PDF parsing and image extraction.
- **Tesseract OCR** — experimental feature for alternative image extraction.
- **TensorFlow** — for image classification using a custom CNN model.
- **RabbitMQ** — for task queueing and communication between services.
- **Amazon S3 (or compatible storage)** — for storing original PDFs and extracted images.
- **MongoDB** — for storing metadata about extracted images and related PDF files.
- **Multithreading** — for parallel processing and improved throughput.

## Architecture
The service operates as a multithreaded FastAPI application that:
- Listens to a RabbitMQ queue for incoming tasks.
- Downloads and processes PDFs from an S3-compatible bucket.
- Extracts and classifies images using PyMuPDF and a custom TensorFlow CNN.
- Uploads processed images back to S3.
- Stores metadata (e.g., image URLs, classification results, source PDF reference) in a MongoDB database.
- Publishes results to a RabbitMQ queue for further processing by downstream services.

## Notes
- The service replaces the previous CLIP-based classifier with a custom TensorFlow CNN model specifically trained for the target image types.
- Experimental extraction using Tesseract is available and can be toggled for specific PDF types if needed.

## Future Improvements
- Support for additional extraction heuristics (e.g., embedded vector graphics detection).
- Horizontal scaling using container orchestration (e.g., Kubernetes).
- Enhancements to the classification model using ensemble or transformer-based approaches.

---

