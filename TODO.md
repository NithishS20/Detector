# TODO: AI-Based Intrusion & Behavior Anomaly Detector Enhancement

## 1. Enhance Backend Anomaly Detection
- [x] Update detect_anomaly function in backend/main.py to include device fingerprint changes, location shifts, and unusual access times.
- [x] Add user session management for account locking and re-authentication.

## 2. Improve Frontend Dashboard
- [x] Enhance frontend/src/App.jsx with visualizations (charts for risk scores, severity distribution).
- [x] Add real-time updates via WebSocket.
- [x] Make UI creative: add animations, better styling, interactive elements (e.g., filter alerts, mark as resolved).

## 3. Integrate Synthetic Data
- [x] Use backend/synthetic_data.py to generate and ingest events for testing.

## 4. Testing and Validation
- [x] Run backend and frontend servers.
- [x] Test with synthetic events to ensure anomalies are detected and alerts are triggered.
- [x] Verify account locking and re-authentication logic.
