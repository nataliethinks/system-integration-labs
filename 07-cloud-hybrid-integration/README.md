# Module 07 – Cloud & Hybrid Integration

This module demonstrates deploying a containerized API
and exposing it through an API Gateway to simulate a
cloud and hybrid integration architecture.

## Overview
A Flask API is containerized using Docker.
NGINX is used as an API Gateway to route external requests
to the backend service. A serverless function is simulated locally.

## Architecture
Client → API Gateway (NGINX) → Dockerized Flask API → Serverless Trigger

## Technologies
Docker & Docker Compose
NGINX (API Gateway)
Python (Flask)

