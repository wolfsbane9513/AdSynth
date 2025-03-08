# AdSynth API Documentation

This document provides comprehensive documentation for the AdSynth API endpoints.

## Base URL

All endpoints are relative to the base URL of your AdSynth server.

## Authentication

Most endpoints require authentication using a Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

### Register User

```http
POST /api/register
```

**Request Body:**
```json
{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
}
```

### Login

```http
POST /api/token
```

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## Campaigns

### Create Campaign

```http
POST /api/campaigns/
```

**Request Body:**
```json
{
    "product_name": "Product Name",
    "product_description": "Product Description",
    "target_audience": "Target Audience Description",
    "key_use_cases": "Key Use Cases",
    "campaign_goal": "Campaign Goal",
    "niche": "Product Niche"
}
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "product_name": "Product Name",
    "product_description": "Product Description",
    "target_audience": "Target Audience Description",
    "key_use_cases": "Key Use Cases",
    "campaign_goal": "Campaign Goal",
    "niche": "Product Niche",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Campaign

```http
GET /api/campaigns/{campaign_id}
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "product_name": "Product Name",
    "product_description": "Product Description",
    "target_audience": "Target Audience Description",
    "key_use_cases": "Key Use Cases",
    "campaign_goal": "Campaign Goal",
    "niche": "Product Niche",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Campaign

```http
PUT /api/campaigns/{campaign_id}
```

**Request Body:**
```json
{
    "product_name": "Updated Product Name",
    "product_description": "Updated Product Description",
    "target_audience": "Updated Target Audience Description",
    "key_use_cases": "Updated Key Use Cases",
    "campaign_goal": "Updated Campaign Goal",
    "niche": "Updated Product Niche"
}
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "product_name": "Updated Product Name",
    "product_description": "Updated Product Description",
    "target_audience": "Updated Target Audience Description",
    "key_use_cases": "Updated Key Use Cases",
    "campaign_goal": "Updated Campaign Goal",
    "niche": "Updated Product Niche",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Delete Campaign

```http
DELETE /api/campaigns/{campaign_id}
```

**Response:**
- Status: 204 No Content

## Ad Scripts

### Generate Ad Script

```http
POST /api/ad-scripts/generate
```

**Request Body:**
```json
{
    "campaign_id": 1,
    "provider": "groq",
    "model": "deepseek-r1-distill-llama-70b"
}
```

**Response:**
```json
{
    "id": 1,
    "campaign_id": 1,
    "provider": "groq",
    "model": "deepseek-r1-distill-llama-70b",
    "content": "Generated ad script content",
    "reddit_references": [
        {
            "title": "Reddit Post Title",
            "content": "Reddit Post Content",
            "url": "https://reddit.com/..."
        }
    ],
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Campaign Ad Scripts

```http
GET /api/ad-scripts/campaign/{campaign_id}
```

**Response:**
```json
[
    {
        "id": 1,
        "campaign_id": 1,
        "provider": "groq",
        "model": "deepseek-r1-distill-llama-70b",
        "content": "Generated ad script content",
        "reddit_references": [
            {
                "title": "Reddit Post Title",
                "content": "Reddit Post Content",
                "url": "https://reddit.com/..."
            }
        ],
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

## Error Responses

In case of errors, the API will return appropriate HTTP status codes along with error messages:

```json
{
    "detail": "Error message description"
}
```

Common error status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Available LLM Providers

The API supports multiple LLM providers for ad script generation:

- OpenAI
- Claude (Anthropic)
- Groq

Each provider may have different models available. Specify the desired provider and model when generating ad scripts.