# Task Entity Implementation

This document describes the Task entity feature added to IdeaGraph.

## Overview

Tasks are work items associated with Ideas. They can be managed through the UI, improved with AI, and exported as GitHub issues.

## Features

### Task Fields

- **ID**: Unique identifier (UUID)
- **Title**: Task title
- **Description**: Detailed task description in Markdown format
- **Repository**: GitHub repository (format: `owner/repository`)
- **KiSuggestions**: AI feedback and suggestions
- **Tags**: List of relevant tags/keywords
- **Status**: Current task status (New, InWork, Review, Ready, Closed)
- **CreatedAt**: Creation timestamp
- **IdeaId**: Reference to the parent Idea

### Task Statuses

1. **New**: Newly created task
2. **InWork**: Task is being worked on
3. **Review**: Task needs review (set by AI if issues detected)
4. **Ready**: Task is ready for implementation (set by AI if approved)
5. **Closed**: Task is completed

### CRUD Operations

Tasks support full CRUD operations through the IdeaDetail page:

- **Create**: Click "New Task" button in the Task tab
- **Read**: View all tasks associated with an Idea
- **Update**: Click "Edit" button on any task
- **Delete**: Click "Delete" button on any task

### AI Content Improvement

The "AI Improve" button triggers an AI workflow that:

1. **Normalizes the description**: Reformats the task description to be clear and structured for developers or AI assistants (Codex/Copilot)
2. **Generates a title**: Creates a concise, descriptive title from the task content
3. **Extracts 5 tags**: Uses the KiGate API `text-keyword-extractor-de` agent to generate relevant German keywords
   - Falls back to OpenAI if KiGate is unavailable
4. **Reviews the task**: AI evaluates if the task is:
   - Meaningful
   - Coherent
   - Feasible
   - Sets status to "Ready" if approved, "Review" if issues found
   - Stores feedback in KiSuggestions field

### GitHub Integration

Tasks with status "Ready" can be exported as GitHub issues:

1. Click "Create GitHub Issue" button
2. The task is sent to the KiGate API `/api/github/create-issue` endpoint
3. A GitHub issue is created in the specified repository
4. The issue number and URL are returned

**Requirements**:
- Task status must be "Ready"
- Repository field must be filled in (format: `owner/repository`)
- KiGate API must be configured

## API Endpoints

### FastAPI Backend

- `POST /task` - Create a new task
- `GET /tasks` - List all tasks
- `GET /tasks/idea/{idea_id}` - List tasks for a specific idea
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task
- `POST /tasks/{task_id}/improve` - Improve task with AI
- `POST /tasks/{task_id}/github-issue` - Create GitHub issue from task

### ASP.NET Core Proxy

- `GET /api/tasks` - List all tasks
- `GET /api/tasks/idea/{ideaId}` - List tasks for a specific idea
- `GET /api/tasks/{id}` - Get a specific task
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `POST /api/tasks/{id}/improve` - Improve task with AI
- `POST /api/tasks/{id}/github-issue` - Create GitHub issue from task

## Configuration

### KiGate API (Required for AI Features)

Add to your `.env` file:

```env
KIGATE_API_URL=https://your-kigate-instance.com
KIGATE_BEARER_TOKEN=your-bearer-token
```

### Client Configuration

The KiGate API configuration is already set up in `appsettings.json`:

```json
{
  "KiGateApi": {
    "KiGateApiUrl": "https://your-kigate-instance.com",
    "KiGateBearerToken": "your-bearer-token-here"
  }
}
```

## Usage Example

1. Open an Idea in the IdeaDetail page
2. Switch to the "Task" tab
3. Click "New Task"
4. Fill in the task details:
   - Title: "Implement user authentication"
   - Description: "Add JWT-based authentication to the API"
   - Repository: "Perculasoft/IdeaGraph"
   - Tags: authentication, security, api
5. Save the task
6. Click "AI Improve" to enhance the task with AI
7. Once status is "Ready", click "Create GitHub Issue"
8. The task is now a GitHub issue!

## Data Storage

Tasks are stored in ChromaDB in the `tasks` collection with:
- Document: Combined title, description, repository, and tags for embedding
- Embeddings: Vector representation for similarity search
- Metadata: All task fields (title, repository, ki_suggestions, tags, status, idea_id, created_at)

## Technical Notes

- Task model renamed to `IdeaTask` to avoid conflicts with `System.Threading.Tasks.Task`
- AI improvement uses OpenAI GPT-4o-mini model
- Tag extraction attempts KiGate first, falls back to OpenAI
- Task descriptions support Markdown formatting
- All AI operations include error handling and fallbacks
