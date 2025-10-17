using IdeaGraph.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Net.Http;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TasksController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<TasksController> _logger;

        public TasksController(IHttpClientFactory httpClientFactory, ILogger<TasksController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<List<IdeaTask>>> GetTasks()
        {
            try
            {
                _logger.LogInformation("Forwarding GET /tasks to FastAPI");
                var response = await _httpClient.GetFromJsonAsync<List<IdeaTask>>($"tasks");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching tasks from FastAPI");
                return StatusCode(500, new { error = "Failed to list tasks", detail = ex.Message });
            }
        }

        [HttpGet("idea/{ideaId}")]
        public async Task<ActionResult<List<IdeaTask>>> GetTasksByIdea(string ideaId)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /tasks/idea/{ideaId} to FastAPI", ideaId);
                var response = await _httpClient.GetFromJsonAsync<List<IdeaTask>>($"tasks/idea/{ideaId}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching tasks for idea {ideaId} from FastAPI", ideaId);
                return StatusCode(500, new { error = "Failed to list tasks for idea", detail = ex.Message });
            }
        }

        [HttpPost]
        public async Task<ActionResult<IdeaTask>> CreateTask([FromBody] TaskCreateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /task to FastAPI: {Title}", request.Title);

                if (string.IsNullOrWhiteSpace(request.Title))
                {
                    return BadRequest(new { error = "Title is required" });
                }

                if (string.IsNullOrWhiteSpace(request.IdeaId))
                {
                    return BadRequest(new { error = "Idea ID is required" });
                }

                var response = await _httpClient.PostAsJsonAsync("task", request);
                response.EnsureSuccessStatusCode();

                var createdTask = await response.Content.ReadFromJsonAsync<IdeaTask>();
                return Ok(createdTask);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating task");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<IdeaTask>> GetTask(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /tasks/{id} to FastAPI", id);
                var response = await _httpClient.GetFromJsonAsync<IdeaTask>($"tasks/{id}");
                
                if (response == null)
                {
                    return NotFound(new { error = "Task not found" });
                }
                
                return Ok(response);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Task {id} not found in FastAPI", id);
                return NotFound(new { error = "Task not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching task {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to get task", detail = ex.Message });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<IdeaTask>> UpdateTask(string id, [FromBody] TaskUpdateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding PUT /tasks/{id} to FastAPI: {Title}", id, request.Title);
                var response = await _httpClient.PutAsJsonAsync($"tasks/{id}", request);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Task not found" });
                }
                
                response.EnsureSuccessStatusCode();
                var updatedTask = await response.Content.ReadFromJsonAsync<IdeaTask>();
                return Ok(updatedTask);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Task {id} not found in FastAPI", id);
                return NotFound(new { error = "Task not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating task {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to update task", detail = ex.Message });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteTask(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding DELETE /tasks/{id} to FastAPI", id);
                var response = await _httpClient.DeleteAsync($"tasks/{id}");
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Task not found" });
                }
                
                response.EnsureSuccessStatusCode();
                return Ok(new { message = "Task deleted successfully", id });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Task {id} not found in FastAPI", id);
                return NotFound(new { error = "Task not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting task {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to delete task", detail = ex.Message });
            }
        }

        [HttpPost("{id}/improve")]
        public async Task<ActionResult<IdeaTask>> ImproveTask(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /tasks/{id}/improve to FastAPI", id);
                var response = await _httpClient.PostAsync($"tasks/{id}/improve", null);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Task not found" });
                }
                
                if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return BadRequest(new { error = "Task has no description to improve", detail = errorContent });
                }
                
                response.EnsureSuccessStatusCode();
                var improvedTask = await response.Content.ReadFromJsonAsync<IdeaTask>();
                return Ok(improvedTask);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Task {id} not found in FastAPI", id);
                return NotFound(new { error = "Task not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error improving task {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to improve task", detail = ex.Message });
            }
        }

        [HttpPost("{id}/github-issue")]
        public async Task<ActionResult<GitHubIssueResponse>> CreateGitHubIssue(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /tasks/{id}/github-issue to FastAPI", id);
                var response = await _httpClient.PostAsync($"tasks/{id}/github-issue", null);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Task not found" });
                }
                
                if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return BadRequest(new { error = "Task is not ready for GitHub issue creation", detail = errorContent });
                }
                
                response.EnsureSuccessStatusCode();
                var issueResponse = await response.Content.ReadFromJsonAsync<GitHubIssueResponse>();
                return Ok(issueResponse);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Task {id} not found in FastAPI", id);
                return NotFound(new { error = "Task not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating GitHub issue for task {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to create GitHub issue", detail = ex.Message });
            }
        }
    }
}
