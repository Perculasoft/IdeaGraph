# Mail Endpoints Testing Guide

This document provides examples for testing the mail endpoints.

## Prerequisites

1. Azure App Registration with:
   - `Mail.Send` permission
   - `Mail.ReadWrite` permission
   - `Mail.ReadWrite.Shared` permission

2. Configure `.env` file:
```env
CLIENT_ID=your-azure-app-client-id
CLIENT_SECRET=your-azure-app-client-secret
TENANT_ID=your-azure-tenant-id
X_API_KEY=your-api-key
```

## Test Send Email

### Using curl

```bash
curl -X POST http://localhost:8000/mail/send \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "sender": "user@example.com",
    "subject": "Test Email from IdeaGraph",
    "body": "<h1>Hello</h1><p>This is a test email sent via Microsoft Graph API.</p>",
    "to": "recipient@example.com",
    "cc": "cc@example.com"
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/mail/send"
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": "your-api-key"
}
data = {
    "sender": "user@example.com",
    "subject": "Test Email from IdeaGraph",
    "body": "<h1>Hello</h1><p>This is a test email.</p>",
    "to": "recipient@example.com",
    "cc": "cc@example.com"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Test Receive Emails

### Using curl

```bash
curl -X GET http://localhost:8000/mail/receive \
  -H "X-Api-Key: your-api-key"
```

### Using Python

```python
import requests

url = "http://localhost:8000/mail/receive"
headers = {
    "X-Api-Key": "your-api-key"
}

response = requests.get(url, headers=headers)
print(response.json())
```

## Expected Responses

### Send Email Success
```json
{
  "message": "Email sent successfully",
  "sender": "user@example.com",
  "to": "recipient@example.com",
  "cc": "cc@example.com",
  "subject": "Test Email from IdeaGraph"
}
```

### Receive Emails Success
```json
{
  "message": "Processed 3 emails",
  "ideas_created": [
    {
      "id": "abc-123",
      "title": "Feature Request: Dark Mode",
      "tags": ["feature", "ui", "accessibility", "design", "enhancement"],
      "email_id": "AAMkADQ..."
    }
  ]
}
```

## Troubleshooting

### Authentication Errors
If you get a 403 error, check:
- CLIENT_ID, CLIENT_SECRET, and TENANT_ID are correct
- Azure App Registration has the required permissions
- Permissions are granted admin consent

### Mail Send Errors
If you get a 500 error when sending:
- Verify the sender has a valid mailbox
- Check if the sender email has SendAs permissions
- Ensure the Azure App has Mail.Send permission

### Mail Receive Errors
If you get a 500 error when receiving:
- Verify the shared mailbox `idea@angermeier.net` exists
- Check if the app has Mail.ReadWrite.Shared permission
- Ensure the Archive folder exists in the mailbox

## Logs

Check the logs for detailed error messages:
- All operations are logged with timestamps
- Errors include full stack traces
- Set LOG_LEVEL=DEBUG in .env for more details
