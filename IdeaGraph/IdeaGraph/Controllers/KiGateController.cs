using IdeaGraph.Models;
using Microsoft.AspNetCore.Mvc;
using System.Net.Http.Headers;

namespace IdeaGraph.Controllers
{
    /// <summary>
    /// Proxy controller for KiGate API (non-admin endpoints only)
    /// </summary>
    [ApiController]
    [Route("api/kigate")]
    public class KiGateController : ControllerBase
    {
        private readonly HttpClient? _httpClient;
        private readonly ILogger<KiGateController> _logger;
        private readonly bool _isConfigured;

        public KiGateController(IHttpClientFactory httpClientFactory, ILogger<KiGateController> logger)
        {
            _logger = logger;
            try
            {
                _httpClient = httpClientFactory.CreateClient("KiGateAPI");
                _isConfigured = _httpClient.BaseAddress != null;
            }
            catch
            {
                _isConfigured = false;
                _httpClient = null;
            }
        }

        private ActionResult? CheckConfiguration()
        {
            if (!_isConfigured || _httpClient == null)
            {
                _logger.LogWarning("KiGate API is not configured");
                return StatusCode(503, new { error = "KiGate API is not configured. Please set KiGateApiUrl in appsettings." });
            }
            return null;
        }

        /// <summary>
        /// Health check endpoint
        /// </summary>
        [HttpGet("health")]
        public async Task<ActionResult<KiGateHealthResponse>> GetHealth([FromQuery] string? api_key = null)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding health check to KiGate API");
                var url = string.IsNullOrEmpty(api_key) ? "health" : $"health?api_key={api_key}";
                var response = await _httpClient.GetFromJsonAsync<KiGateHealthResponse>(url);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking KiGate API health");
                return StatusCode(500, new { error = "Failed to check health", detail = ex.Message });
            }
        }

        /// <summary>
        /// Get all agents
        /// </summary>
        [HttpGet("agents")]
        public async Task<ActionResult<List<AgentInfo>>> GetAgents([FromQuery] string? api_key = null)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding get agents request to KiGate API");
                var url = string.IsNullOrEmpty(api_key) ? "api/agents" : $"api/agents?api_key={api_key}";
                var response = await _httpClient.GetFromJsonAsync<List<AgentInfo>>(url);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching agents from KiGate API");
                return StatusCode(500, new { error = "Failed to get agents", detail = ex.Message });
            }
        }

        /// <summary>
        /// OpenAI API endpoint
        /// </summary>
        [HttpPost("openai")]
        public async Task<ActionResult<AiApiResult>> PostOpenAI([FromBody] AiApiRequest request)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding OpenAI request to KiGate API");
                var response = await _httpClient.PostAsJsonAsync("api/openai", request);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<AiApiResult>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error calling OpenAI via KiGate API");
                return StatusCode(500, new { error = "Failed to call OpenAI", detail = ex.Message });
            }
        }

        /// <summary>
        /// Execute agent
        /// </summary>
        [HttpPost("agent/execute")]
        public async Task<ActionResult<AgentExecutionResponse>> ExecuteAgent([FromBody] AgentExecutionRequest request)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding agent execution to KiGate API: {AgentName}", request.AgentName);
                var response = await _httpClient.PostAsJsonAsync("agent/execute", request);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<AgentExecutionResponse>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error executing agent via KiGate API");
                return StatusCode(500, new { error = "Failed to execute agent", detail = ex.Message });
            }
        }

        /// <summary>
        /// Gemini API endpoint
        /// </summary>
        [HttpPost("gemini")]
        public async Task<ActionResult<AiApiResult>> PostGemini([FromBody] AiApiRequest request)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding Gemini request to KiGate API");
                var response = await _httpClient.PostAsJsonAsync("api/gemini", request);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<AiApiResult>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error calling Gemini via KiGate API");
                return StatusCode(500, new { error = "Failed to call Gemini", detail = ex.Message });
            }
        }

        /// <summary>
        /// Claude API endpoint
        /// </summary>
        [HttpPost("claude")]
        public async Task<ActionResult<AiApiResult>> PostClaude([FromBody] AiApiRequest request)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding Claude request to KiGate API");
                var response = await _httpClient.PostAsJsonAsync("api/claude", request);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<AiApiResult>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error calling Claude via KiGate API");
                return StatusCode(500, new { error = "Failed to call Claude", detail = ex.Message });
            }
        }

        /// <summary>
        /// Create GitHub issue
        /// </summary>
        [HttpPost("github/create-issue")]
        public async Task<ActionResult<GitHubIssueResponse>> CreateGitHubIssue([FromBody] GitHubIssueRequest request)
        {
            var configError = CheckConfiguration();
            if (configError != null) return configError;

            try
            {
                _logger.LogInformation("Forwarding GitHub issue creation to KiGate API: {Repository}", request.Repository);
                var response = await _httpClient.PostAsJsonAsync("api/github/create-issue", request);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadFromJsonAsync<GitHubIssueResponse>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating GitHub issue via KiGate API");
                return StatusCode(500, new { error = "Failed to create GitHub issue", detail = ex.Message });
            }
        }
    }
}
