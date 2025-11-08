# API Reference

This file documents the HTTP endpoints exposed by the Flask server (`main.py`). All endpoints are relative to the server base (e.g., `http://localhost:5000`).

## 1) GET /

- Description: Serves the main HTML page (`templates/index.html`).
- Response: HTML page (200)

## 2) GET /video_feed

- Description: Streams MJPEG video frames. Intended to be used as the `src` of an `<img>` tag.
- Response: `multipart/x-mixed-replace; boundary=frame` continuous stream of JPEG frames.
- Example usage in HTML:

```html
<img src="/video_feed" alt="camera stream">
```

## 3) GET /captured

- Description: Returns a JSON array of filenames (JPGs) in `static/captured/`.
- Response example:

```json
[
  "a3f7c2d1_20251108-143052.jpg",
  "b8e9d4f2_20251108-144123.jpg"
]
```

## 4) POST /set_detection

- Description: Toggle detection on/off at runtime.
- Request:
  - Content-Type: `application/json`
  - Body: `{"enabled": true}` or `{"enabled": false}`
- Successful response: `200 OK` with JSON `{"enabled": true}` (or false)
- Error response: `400 Bad Request` if `enabled` missing or not a boolean.
- Example (curl):

```bash
curl -X POST http://localhost:5000/set_detection -H "Content-Type: application/json" -d '{"enabled":false}'
```

## 5) GET /status

- Description: Returns whether detection is currently enabled.
- Response example:

```json
{"enabled": true}
```

## 6) GET /current_emotions

- Description: Returns the latest computed emotions and metadata.
- Response schema:

```json
{
  "enabled": true,
  "timestamp": "20251108-143052",
  "emotions": {
    "angry": 15.2,
    "disgust": 2.1,
    "fear": 5.8,
    "happy": 45.3,
    "sad": 12.4,
    "surprise": 8.7,
    "neutral": 10.5
  },
  "main_emotion": "happy",
  "danger_score": 23.1
}
```

Notes:
- `emotions` may be `null` if no analysis has been performed yet.
- `danger_score` equals the sum of `angry + fear + disgust` percentages (consistent with `modules/face_analysis.py`).

---

## Error handling
- Most endpoints return `400` for malformed requests and `500` for unexpected server errors. The responses contain a JSON `{"error": "message"}` describing the issue.

---

## Integration tips
- Use periodic polling of `/current_emotions` for dashboards.
- Use the MJPEG stream for low-latency embedding in HTML pages.
- For programmatic control, POST `/set_detection` from your automation scripts or UIs.

End of API reference.
