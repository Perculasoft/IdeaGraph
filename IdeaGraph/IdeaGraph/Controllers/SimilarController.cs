using Microsoft.AspNetCore.Mvc;
using IdeaGraph.Models;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SimilarController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<SimilarController> _logger;

        public SimilarController(IHttpClientFactory httpClientFactory, ILogger<SimilarController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet("{ideaId}")]
        public async Task<ActionResult<List<SimilarIdea>>> GetSimilar(string ideaId, [FromQuery] int k = 5)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /similar/{ideaId} to FastAPI with k={k}", ideaId, k);
                var response = await _httpClient.GetAsync($"similar/{ideaId}?k={k}");
                
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    _logger.LogWarning("Idea {ideaId} not found in FastAPI for similarity search", ideaId);
                    return NotFound(new { error = "Idea not found" });
                }
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("FastAPI returned error {StatusCode} for similar ideas: {Error}", response.StatusCode, errorContent);
                    return StatusCode((int)response.StatusCode, new { error = "Failed to find similar ideas", detail = errorContent });
                }
                
                var similarIdeas = await response.Content.ReadFromJsonAsync<List<SimilarIdea>>();
                return Ok(similarIdeas);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching similar ideas from FastAPI");
                return StatusCode(500, new { error = "Failed to find similar ideas", detail = ex.Message });
            }
        }
    }
}
