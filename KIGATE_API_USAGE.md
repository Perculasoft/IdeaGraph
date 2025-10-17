# KiGate API Integration - Usage Examples

This document provides examples of how to use the KiGate API integration in the IdeaGraph project.

## Configuration

First, configure the KiGate API in your `appsettings.json`:

```json
{
  "KiGateApi": {
    "KiGateApiUrl": "https://your-kigate-instance.com",
    "KiGateBearerToken": "your-bearer-token-here"
  }
}
```

## Using KiGateService in Blazor Components

### Inject the Service

```csharp
@inject KiGateService KiGateService
```

### Check Health

```csharp
var health = await KiGateService.GetHealthAsync();
if (health != null && health.Status == "ok")
{
    Console.WriteLine("KiGate API is healthy");
}
```

### Get Available Agents

```csharp
var agents = await KiGateService.GetAgentsAsync();
foreach (var agent in agents)
{
    Console.WriteLine($"Agent: {agent.Name} - {agent.Description}");
    Console.WriteLine($"Provider: {agent.Provider}, Model: {agent.Model}");
}
```

### Execute an Agent

```csharp
var request = new AgentExecutionRequest
{
    AgentName = "code-reviewer",
    Message = "Please review this code snippet...",
    Provider = "openai",
    Model = "gpt-4",
    UserId = "user123"
};

var response = await KiGateService.ExecuteAgentAsync(request);
if (response != null && response.Result != null)
{
    Console.WriteLine($"Job ID: {response.JobId}");
    Console.WriteLine($"Response: {response.Result.Content}");
    Console.WriteLine($"Tokens used: {response.Result.Usage?.TotalTokens}");
}
```

### Call OpenAI Directly

```csharp
var request = new AiApiRequest
{
    Messages = new List<AiMessage>
    {
        new AiMessage 
        { 
            Role = "user", 
            Content = "Explain quantum computing in simple terms" 
        }
    },
    Model = "gpt-4",
    Temperature = 0.7,
    MaxTokens = 500
};

var response = await KiGateService.CallOpenAIAsync(request);
if (response != null)
{
    Console.WriteLine($"Response: {response.Content}");
    Console.WriteLine($"Model: {response.Model}");
}
```

### Create a GitHub Issue

```csharp
var request = new GitHubIssueRequest
{
    Repository = "owner/repository",
    Text = "Found a bug in the application where the login form doesn't validate email addresses properly.",
    UserId = "user123"
};

var response = await KiGateService.CreateGitHubIssueAsync(request);
if (response != null && response.Error == null)
{
    Console.WriteLine($"Created issue #{response.IssueNumber}");
    Console.WriteLine($"Title: {response.Title}");
    Console.WriteLine($"URL: {response.Url}");
}
```

## Using KiGate API via HTTP Endpoints

You can also call the KiGate API endpoints directly from external applications or tools.

### Health Check

```bash
curl -X GET "https://your-ideagraph.com/api/kigate/health"
```

### Get Agents

```bash
curl -X GET "https://your-ideagraph.com/api/kigate/agents"
```

### Execute Agent

```bash
curl -X POST "https://your-ideagraph.com/api/kigate/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "code-reviewer",
    "message": "Review this code...",
    "provider": "openai",
    "model": "gpt-4"
  }'
```

### Call OpenAI

```bash
curl -X POST "https://your-ideagraph.com/api/kigate/openai" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    "model": "gpt-4",
    "temperature": 0.7
  }'
```

### Create GitHub Issue

```bash
curl -X POST "https://your-ideagraph.com/api/kigate/github/create-issue" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "owner/repo",
    "text": "Description of the issue to create",
    "user_id": "user123"
  }'
```

## Error Handling

Always check for errors when using the KiGate API:

```csharp
var response = await KiGateService.ExecuteAgentAsync(request);
if (response == null)
{
    // Service call failed - check logs
    Console.WriteLine("Failed to call KiGate API");
}
else if (response.Error != null)
{
    // API returned an error
    Console.WriteLine($"Error: {response.Error}");
}
else if (response.Result != null)
{
    // Success
    Console.WriteLine($"Result: {response.Result.Content}");
}
```

## Configuration Status

If the KiGate API is not configured, all endpoints will return:

```json
{
  "error": "KiGate API is not configured. Please set KiGateApiUrl in appsettings."
}
```

with HTTP status code 503 (Service Unavailable).

## Best Practices

1. **Always check for null responses** - Network issues or configuration problems can cause null responses
2. **Handle errors gracefully** - Check the `Error` property in responses
3. **Use appropriate timeouts** - The default timeout is 60 seconds
4. **Monitor token usage** - Check the `Usage` property to track AI API costs
5. **Secure your Bearer token** - Never commit tokens to source control, use environment variables or secure configuration
6. **Test with health endpoint first** - Verify connectivity before using other endpoints

## Security Notes

- The KiGate API uses Bearer token authentication
- The token is configured in `appsettings.json` and automatically added to all requests
- Admin endpoints (`/admin/*`) are not exposed through the proxy for security
- All API calls are logged for audit purposes
