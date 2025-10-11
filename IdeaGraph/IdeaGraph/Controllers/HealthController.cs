using Microsoft.AspNetCore.Mvc;
using IdeaGraph.Models;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class HealthController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<HealthController> _logger;

        public HealthController(IHttpClientFactory httpClientFactory, ILogger<HealthController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<HealthResponse>> GetHealth()
        {
            try
            {
                _logger.LogInformation("Forwarding health check to FastAPI");
                var response = await _httpClient.GetFromJsonAsync<HealthResponse>("health");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking FastAPI health");
                return StatusCode(500, new { error = "Failed to check health", detail = ex.Message });
            }
        }
    }
}
