# API Reference

Complete documentation for SarcasmAI REST API endpoints.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Endpoints](#endpoints)
- [Examples](#examples)
- [Error Handling](#error-handling)

---

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

**Current**: No authentication required (open API)

**Future**: Token-based authentication may be implemented.

---

## Response Format

All responses are JSON formatted.

### Success Response (200 OK)

```json
{
  "id": "unique-analysis-id",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.5,
    "reasoning": "Optional reasoning from Claude",
    "modality_scores": {
      "text": 0.82,
      "image": null,
      "audio": null,
      "video": null,
      "emoji": 0.87,
      "claude": 0.72
    },
    "final_score": 0.80
  }
}
```

### Error Response (400/500)

```json
{
  "error": "Error message describing what went wrong",
  "status": 400
}
```

---

## Endpoints

### 1. Analyze Content

**Endpoint**: `POST /api/analyze/`

**Description**: Submit content for sarcasm analysis across multiple modalities.

**Request Headers**:
```
Content-Type: multipart/form-data
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Optional | Text content to analyze (max 5000 chars) |
| `image` | file | Optional | Image file (JPG, PNG, max 10MB) |
| `audio` | file | Optional | Audio file (MP3, WAV, max 25MB) |
| `video` | file | Optional | Video file (MP4, max 100MB) |

**At least one input is required.**

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.5,
    "reasoning": "The expression suggests frustration with a routine event...",
    "modality_scores": {
      "text": 0.82,
      "image": null,
      "audio": null,
      "video": null,
      "emoji": 0.87,
      "claude": 0.72
    },
    "final_score": 0.80
  }
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (missing inputs, invalid file format)
- `413`: File too large
- `500`: Server error

---

### 2. Get Analysis Result

**Endpoint**: `GET /api/result/<id>/`

**Description**: Retrieve a previously stored analysis result by ID.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Analysis ID from analyze endpoint |

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-26T10:30:45Z",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.5,
    "reasoning": "...",
    "modality_scores": {
      "text": 0.82,
      "image": null,
      "audio": null,
      "video": null,
      "emoji": 0.87,
      "claude": 0.72
    },
    "final_score": 0.80
  }
}
```

**Status Codes**:
- `200`: Success
- `404`: Analysis ID not found
- `500`: Server error

---

### 3. Get Analysis History

**Endpoint**: `GET /api/history/`

**Description**: Get list of all previously submitted analyses.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of results to return (max 100) |
| `offset` | integer | 0 | Number of results to skip (for pagination) |

**Response** (200 OK):
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/history/?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-05-26T10:30:45Z",
      "text_preview": "Oh great, another Monday",
      "is_sarcastic": true,
      "confidence": 78.5
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2026-05-26T10:25:30Z",
      "text_preview": "That's just perfect",
      "is_sarcastic": true,
      "confidence": 82.3
    }
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid parameters
- `500`: Server error

---

### 4. Ablation Analysis

**Endpoint**: `GET /api/ablation/<id>/`

**Description**: Get per-modality breakdown and importance scores for a specific analysis.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Analysis ID |

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "modality_importance": {
    "text": {
      "score": 0.82,
      "weight": 0.25,
      "contribution": 0.205,
      "ranking": 2
    },
    "image": {
      "score": null,
      "weight": 0.20,
      "contribution": 0.0,
      "ranking": null
    },
    "audio": {
      "score": null,
      "weight": 0.12,
      "contribution": 0.0,
      "ranking": null
    },
    "video": {
      "score": null,
      "weight": 0.10,
      "contribution": 0.0,
      "ranking": null
    },
    "emoji": {
      "score": 0.87,
      "weight": 0.08,
      "contribution": 0.0696,
      "ranking": 1
    },
    "claude": {
      "score": 0.72,
      "weight": 0.35,
      "contribution": 0.252,
      "ranking": 1
    }
  },
  "final_score": 0.80,
  "dominant_modality": "claude"
}
```

**Status Codes**:
- `200`: Success
- `404`: Analysis ID not found
- `500`: Server error

---

### 5. Health Check

**Endpoint**: `GET /api/health/`

**Description**: Check API and service health status.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "models": {
    "text": "loaded",
    "image": "loaded",
    "audio": "loaded",
    "video": "loaded",
    "emoji": "ready",
    "claude": "configured"
  },
  "database": "connected",
  "timestamp": "2026-05-26T10:30:45Z"
}
```

**Status Codes**:
- `200`: All systems healthy
- `503`: Service unavailable

---

## Examples

### Example 1: Text Analysis Only

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -F "text=Oh great, another Monday"
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.4,
    "modality_scores": {
      "text": 0.82,
      "emoji": null,
      "claude": 0.72
    },
    "final_score": 0.78
  }
}
```

### Example 2: Text with Emoji

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -F "text=Oh great, another meeting 🙄"
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "result": {
    "is_sarcastic": true,
    "confidence": 82.3,
    "modality_scores": {
      "text": 0.82,
      "emoji": 0.87,
      "claude": 0.75
    },
    "final_score": 0.82
  }
}
```

### Example 3: Multi-modal Analysis

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -F "text=This is wonderful" \
  -F "image=@sarcasm.jpg" \
  -F "audio=@tone.wav"
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "result": {
    "is_sarcastic": true,
    "confidence": 85.6,
    "reasoning": "Text appears positive but sarcastic based on tone analysis...",
    "modality_scores": {
      "text": 0.65,
      "image": 0.72,
      "audio": 0.88,
      "emoji": null,
      "claude": 0.82
    },
    "final_score": 0.82
  }
}
```

### Example 4: Retrieve Result

```bash
curl -X GET http://localhost:8000/api/result/550e8400-e29b-41d4-a716-446655440000/
```

### Example 5: Get Analysis History

```bash
curl -X GET "http://localhost:8000/api/history/?limit=10"
```

### Example 6: Ablation Analysis

```bash
curl -X GET http://localhost:8000/api/ablation/550e8400-e29b-41d4-a716-446655440000/
```

### Example 7: Health Check

```bash
curl -X GET http://localhost:8000/api/health/
```

---

## Error Handling

### Common Error Codes

#### 400 Bad Request

```json
{
  "error": "At least one input (text, image, audio, video) is required",
  "status": 400
}
```

**Causes**:
- No input provided
- Invalid file format
- File too large
- Invalid text length

#### 404 Not Found

```json
{
  "error": "Analysis with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "status": 404
}
```

**Causes**:
- Invalid analysis ID
- Analysis has been deleted
- ID from different database instance

#### 413 Payload Too Large

```json
{
  "error": "File size exceeds maximum (25MB for audio)",
  "status": 413
}
```

**File Size Limits**:
- Text: 5,000 characters
- Image: 10 MB
- Audio: 25 MB
- Video: 100 MB

#### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred. Check server logs.",
  "status": 500
}
```

**Causes**:
- Server crash
- Model loading failure
- Database connection error
- API quota exceeded

---

## Rate Limiting

**Current**: No rate limiting (open API)

**Future**: May implement:
- 100 requests per minute (per IP)
- 1,000 requests per day (per API key)

---

## Response Time

Typical response times by modality:

| Modality | Time |
|----------|------|
| Text Only | 0.5-1s |
| Text + Emoji | 0.7-1.2s |
| Text + Image | 1-2s |
| Text + Audio | 2-5s |
| Text + Video | 3-7s |
| All Modalities | 5-10s |
| + Claude API | +2-5s |

---

## Webhooks

**Not currently implemented** - results are stored in database and can be polled.

---

## SDKs

No official SDKs yet, but HTTP clients work with any language:

**Python**:
```python
import requests

response = requests.post(
    'http://localhost:8000/api/analyze/',
    data={'text': 'Oh great, another Monday'}
)
result = response.json()
print(f"Sarcastic: {result['result']['is_sarcastic']}")
```

**JavaScript**:
```javascript
const formData = new FormData();
formData.append('text', 'Oh great, another Monday');

fetch('http://localhost:8000/api/analyze/', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

**cURL** (already shown above)

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Support for text, image, audio, video, emoji modalities
- Ablation endpoint
- Health check endpoint
- History endpoint

---

## Support

For API issues:
- Check error messages and status codes above
- Review examples section
- Open GitHub issue: https://github.com/YOUR_USERNAME/sarcasm-ai/issues

**Last Updated**: 2026-05-26
