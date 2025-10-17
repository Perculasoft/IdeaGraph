using IdeaGraph.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Net.Http;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class IdeasController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<IdeasController> _logger;

        public IdeasController(IHttpClientFactory httpClientFactory, ILogger<IdeasController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<List<Idea>>> GetIdeas()
        {
            try
            {
                _logger.LogInformation("Forwarding GET /ideas to FastAPI");
                var response = await _httpClient.GetAsync("ideas");
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogWarning("FastAPI returned {StatusCode} when fetching ideas", response.StatusCode);
                    return StatusCode((int)response.StatusCode, new { error = "Failed to list ideas", detail = $"FastAPI returned {response.StatusCode}" });
                }
                
                var ideas = await response.Content.ReadFromJsonAsync<List<Idea>>();
                return Ok(ideas);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "HTTP error fetching ideas from FastAPI");
                return StatusCode(500, new { error = "Failed to list ideas", detail = ex.Message });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching ideas from FastAPI");
                return StatusCode(500, new { error = "Failed to list ideas", detail = ex.Message });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Idea>> CreateIdea([FromBody] IdeaCreateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /idea to FastAPI: {Title}", request.Title);

                if (string.IsNullOrWhiteSpace(request.Title))
                {
                    return BadRequest(new { error = "Title is required" });
                }

                var response = await _httpClient.PostAsJsonAsync("idea", request);
                response.EnsureSuccessStatusCode();

                var createdIdea = await response.Content.ReadFromJsonAsync<Idea>();
                return Ok(createdIdea);

             
            }
            catch (Exception ex)
            {
               
                _logger.LogInformation("Forwarding GET /ideas to FastAPI");
                var response = await _httpClient.GetFromJsonAsync<List<Idea>>("ideas");
                return StatusCode(500, new { error = ex.Message });
            }
          
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Idea>> GetIdea(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /ideas/{id} to FastAPI", id);
                var response = await _httpClient.GetFromJsonAsync<Idea>($"ideas/{id}");
                
                if (response == null)
                {
                    return NotFound(new { error = "Idea not found" });
                }
                
                return Ok(response);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Idea {id} not found in FastAPI", id);
                return NotFound(new { error = "Idea not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching idea {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to get idea", detail = ex.Message });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Idea>> UpdateIdea(string id, [FromBody] IdeaUpdateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding PUT /ideas/{id} to FastAPI: {Title}", id, request.Title);
                var response = await _httpClient.PutAsJsonAsync($"ideas/{id}", request);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Idea not found" });
                }
                
                response.EnsureSuccessStatusCode();
                var updatedIdea = await response.Content.ReadFromJsonAsync<Idea>();
                return Ok(updatedIdea);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Idea {id} not found in FastAPI", id);
                return NotFound(new { error = "Idea not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating idea {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to update idea", detail = ex.Message });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteIdea(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding DELETE /ideas/{id} to FastAPI", id);
                var response = await _httpClient.DeleteAsync($"ideas/{id}");
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Idea not found" });
                }
                
                response.EnsureSuccessStatusCode();
                return Ok(new { message = "Idea deleted successfully", id });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Idea {id} not found in FastAPI", id);
                return NotFound(new { error = "Idea not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting idea {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to delete idea", detail = ex.Message });
            }
        }

        [HttpPost("{id}/enhance")]
        public async Task<ActionResult<Idea>> EnhanceIdea(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /ideas/{id}/enhance to FastAPI", id);
                var response = await _httpClient.PostAsync($"ideas/{id}/enhance", null);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Idea not found" });
                }
                
                if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return BadRequest(new { error = "Idea has no description to enhance", detail = errorContent });
                }
                
                response.EnsureSuccessStatusCode();
                var enhancedIdea = await response.Content.ReadFromJsonAsync<Idea>();
                return Ok(enhancedIdea);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Idea {id} not found in FastAPI", id);
                return NotFound(new { error = "Idea not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error enhancing idea {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to enhance idea", detail = ex.Message });
            }
        }
    }
}
