using IdeaGraph.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Net.Http;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SectionsController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<SectionsController> _logger;

        public SectionsController(IHttpClientFactory httpClientFactory, ILogger<SectionsController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<List<Section>>> GetSections()
        {
            try
            {
                _logger.LogInformation("Forwarding GET /sections to FastAPI");
                var response = await _httpClient.GetAsync("sections");
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    _logger.LogInformation("FastAPI returned 404 when listing sections - returning empty list");
                    return Ok(new List<Section>());
                }

                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogWarning("FastAPI returned {StatusCode} when fetching sections", response.StatusCode);
                    return StatusCode((int)response.StatusCode, new { error = "Failed to list sections", detail = $"FastAPI returned {response.StatusCode}" });
                }

                var sections = await response.Content.ReadFromJsonAsync<List<Section>>();
                return Ok(sections ?? new List<Section>());
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "HTTP error fetching sections from FastAPI");
                return StatusCode(500, new { error = "Failed to list sections", detail = ex.Message });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching sections from FastAPI");
                return StatusCode(500, new { error = "Failed to list sections", detail = ex.Message });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Section>> CreateSection([FromBody] SectionCreateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /sections to FastAPI: {Name}", request.Name);

                if (string.IsNullOrWhiteSpace(request.Name))
                {
                    return BadRequest(new { error = "Name is required" });
                }

                var response = await _httpClient.PostAsJsonAsync("sections", request);
                response.EnsureSuccessStatusCode();

                var createdSection = await response.Content.ReadFromJsonAsync<Section>();
                return Ok(createdSection);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating section in FastAPI");
                return StatusCode(500, new { error = "Failed to create section", detail = ex.Message });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Section>> GetSection(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /sections/{id} to FastAPI", id);
                var response = await _httpClient.GetFromJsonAsync<Section>($"sections/{id}");
                
                if (response == null)
                {
                    return NotFound(new { error = "Section not found" });
                }
                
                return Ok(response);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Section {id} not found in FastAPI", id);
                return NotFound(new { error = "Section not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching section {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to get section", detail = ex.Message });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Section>> UpdateSection(string id, [FromBody] SectionUpdateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding PUT /sections/{id} to FastAPI: {Name}", id, request.Name);
                var response = await _httpClient.PutAsJsonAsync($"sections/{id}", request);
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Section not found" });
                }
                
                response.EnsureSuccessStatusCode();
                var updatedSection = await response.Content.ReadFromJsonAsync<Section>();
                return Ok(updatedSection);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Section {id} not found in FastAPI", id);
                return NotFound(new { error = "Section not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating section {id} in FastAPI", id);
                return StatusCode(500, new { error = "Failed to update section", detail = ex.Message });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteSection(string id)
        {
            try
            {
                _logger.LogInformation("Forwarding DELETE /sections/{id} to FastAPI", id);
                var response = await _httpClient.DeleteAsync($"sections/{id}");
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(new { error = "Section not found" });
                }
                
                response.EnsureSuccessStatusCode();
                return Ok(new { message = "Section deleted successfully", id });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                _logger.LogWarning("Section {id} not found in FastAPI", id);
                return NotFound(new { error = "Section not found" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting section {id} from FastAPI", id);
                return StatusCode(500, new { error = "Failed to delete section", detail = ex.Message });
            }
        }
    }
}
