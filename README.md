# Geofence Alert & Logging System - AWS Serverless

**Independent Project** | **July 2025**  

A serverless geofencing alert and logging system built with AWS Lambda, DynamoDB, and SNS. This project simulates GPS devices and demonstrates real-time geofence monitoring, automated notifications, and event logging without managing any servers.  

---

## Project Overview  

This project simulates real-time GPS devices sending location updates to an AWS Lambda function. The Lambda function evaluates whether a device is inside or outside a predefined geofence using the Haversine formula, logs the event in DynamoDB, and sends immediate email alerts via SNS whenever a geofence event occurs.  

---

## Features  

- **Serverless Architecture:** Uses AWS Lambda, DynamoDB, and SNS—no servers to manage.  
- **Real-Time Geofence Monitoring:** Detects when a device enters or exits a geofenced area.  
- **Event Logging:** Stores device ID, coordinates, geofence status, and timestamp in DynamoDB for historical tracking.  
- **Automated Alerts:** Sends email notifications via SNS in real-time for geofence events.  
- **IoT Simulation:** Simulates GPS device updates without requiring physical devices.  

---

## Architecture  

1. **Simulated GPS Device** – Sends location data (latitude, longitude, device ID) to the Lambda function.  
2. **AWS Lambda** – Processes incoming events, calculates distance using the Haversine formula, determines geofence status, logs events to DynamoDB, and triggers SNS alerts.  
3. **DynamoDB** – Stores a historical record of all geofence events.  
4. **SNS (Simple Notification Service)** – Sends real-time email notifications when a device enters or exits the geofence.

---

## Significance

This project demonstrates how serverless AWS services can be combined to build a scalable geofencing solution. The simulation of GPS devices and automating monitoring, logging, and alerting, eliminates the need for manual oversight/infrastructure management. The design is fully scalable, from a single simulated device to thousands, making it applicable for real world IoT applications that require real-time tracking/notifications.

