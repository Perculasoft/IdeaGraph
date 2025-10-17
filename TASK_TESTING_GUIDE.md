# Task Entity Implementation - Testing Guide

## What Was Implemented

This implementation adds a complete Task management system to IdeaGraph with AI-powered content improvement and GitHub integration.

## Testing Checklist

### Prerequisites
Before testing, ensure:
1. FastAPI backend is running with ChromaDB Cloud connection
2. OpenAI API key is configured in `.env`
3. KiGate API URL and Bearer token are configured (optional, for AI tag extraction and GitHub features)
4. Blazor frontend is running

### Manual Testing Steps

#### 1. Basic Task CRUD
- [ ] Open any Idea in the IdeaDetail page
- [ ] Switch to the "Task" tab
- [ ] Click "New Task" button
- [ ] Fill in task details:
  - Title: "Test Task"
  - Description: "This is a test task description with some details"
  - Repository: "owner/repo"
  - Add tags manually
  - Select status
- [ ] Save the task
- [ ] Verify task appears in the list
- [ ] Click "Edit" on the task
- [ ] Modify the task details
- [ ] Save changes
- [ ] Verify changes are reflected
- [ ] Click "Delete" on the task
- [ ] Verify task is removed

#### 2. AI Content Improvement
- [ ] Create a new task with a rough description:
  ```
  Title: "Login feature"
  Description: "need to add login with password and email maybe also google login would be nice"
  Repository: "test/repo"
  ```
- [ ] Click "AI Improve" button
- [ ] Wait for AI processing (may take 10-30 seconds)
- [ ] Verify:
  - [ ] Description is reformatted and improved
  - [ ] Title is auto-generated or improved
  - [ ] 5 tags are automatically added
  - [ ] Status is set to "Ready" or "Review"
  - [ ] If status is "Review", check KiSuggestions for AI feedback

#### 3. GitHub Issue Creation
- [ ] Create a task and improve it with AI until status is "Ready"
- [ ] Ensure Repository field is filled (e.g., "Perculasoft/IdeaGraph")
- [ ] Click "Create GitHub Issue" button
- [ ] Verify:
  - [ ] Success message appears with issue number
  - [ ] Check GitHub repository for the new issue
  - [ ] Issue title and description match the task

#### 4. Edge Cases
- [ ] Try creating a task without a title (should show validation error)
- [ ] Try improving a task with no description (should show error)
- [ ] Try creating GitHub issue from a task not in "Ready" status (should show error)
- [ ] Try creating GitHub issue from a task without repository (should show error)
- [ ] Switch between "Similar" and "Task" tabs to verify tasks load correctly

#### 5. Multiple Tasks
- [ ] Create several tasks for the same idea
- [ ] Verify they all appear in the list
- [ ] Verify they are sorted by creation date
- [ ] Test editing and deleting different tasks

### API Testing

You can test the API endpoints directly using curl or a tool like Postman:

#### Create Task
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d '{
    "title": "Test Task",
    "description": "Test description",
    "repository": "owner/repo",
    "tags": ["test", "api"],
    "status": "New",
    "idea_id": "YOUR_IDEA_ID"
  }'
```

#### List Tasks for Idea
```bash
curl -X GET "http://localhost:8000/tasks/idea/{idea_id}" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### Improve Task
```bash
curl -X POST "http://localhost:8000/tasks/{task_id}/improve" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### Create GitHub Issue
```bash
curl -X POST "http://localhost:8000/tasks/{task_id}/github-issue" \
  -H "X-Api-Key: YOUR_API_KEY"
```

## Known Limitations

1. **KiGate API Dependency**: Tag extraction and GitHub issue creation require KiGate API to be configured. If unavailable:
   - Tag extraction falls back to OpenAI
   - GitHub issue creation will fail with error 503

2. **AI Processing Time**: AI improvement can take 10-30 seconds depending on:
   - OpenAI API response time
   - KiGate API availability
   - Network latency

3. **Markdown Editing**: The task description field is a simple textarea. For better Markdown editing, consider integrating a Markdown editor component in the future.

4. **No Confirmation Dialogs**: Delete operations happen immediately without confirmation. Consider adding confirmation modals in production.

## Troubleshooting

### Task Creation Fails
- Check FastAPI logs for errors
- Verify ChromaDB connection is working
- Ensure Idea ID exists

### AI Improvement Fails
- Check OpenAI API key is configured
- Check FastAPI logs for detailed error messages
- Verify OpenAI API quota/limits

### GitHub Issue Creation Fails
- Verify KiGate API is configured and running
- Check task status is "Ready"
- Verify repository format is correct (owner/repo)
- Check KiGate API logs

### Tasks Don't Load
- Check browser console for errors
- Verify API endpoints are accessible
- Check network tab for failed requests

## Performance Notes

- Tasks are embedded using OpenAI embeddings (same as Ideas)
- Each task improvement makes multiple API calls:
  1. OpenAI for description improvement and title generation
  2. KiGate for tag extraction (or OpenAI fallback)
  3. OpenAI for task review
  4. ChromaDB update
- Consider implementing rate limiting for AI operations in production
- Task list loads lazily when tab is activated

## Future Enhancements

Potential improvements for consideration:
- [ ] Add rich Markdown editor for task descriptions
- [ ] Implement task templates
- [ ] Add task assignment/ownership
- [ ] Add task due dates and reminders
- [ ] Implement task search and filtering
- [ ] Add task comments/discussion
- [ ] Implement task dependencies
- [ ] Add bulk operations (delete multiple, batch improve)
- [ ] Add task export formats (PDF, CSV)
- [ ] Implement task analytics and reporting
