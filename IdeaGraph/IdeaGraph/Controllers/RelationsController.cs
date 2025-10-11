using Microsoft.AspNetCore.Mvc;
using IdeaGraph.Models;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RelationsController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<RelationsController> _logger;

        public RelationsController(IHttpClientFactory httpClientFactory, ILogger<RelationsController> logger)
        {
            _httpClient = httpClientFactory.CreateClient("FastAPI");
            _logger = logger;
        }

        [HttpGet("{ideaId}")]
        public async Task<ActionResult<List<Relation>>> GetRelations(string ideaId)
        {
            try
            {
                _logger.LogInformation("Forwarding GET /relations/{ideaId} to FastAPI", ideaId);
                var response = await _httpClient.GetFromJsonAsync<List<Relation>>($"relations/{ideaId}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching relations from FastAPI");
                return StatusCode(500, new { error = "Failed to list relations", detail = ex.Message });
            }
        }

        [HttpPost]
        [Route("/api/relation")]
        public async Task<ActionResult<Relation>> CreateRelation([FromBody] RelationCreateRequest request)
        {
            try
            {
                _logger.LogInformation("Forwarding POST /relation to FastAPI: {sourceId} -> {targetId}", 
                    request.SourceId, request.TargetId);
                var response = await _httpClient.PostAsJsonAsync("relation", request);
                response.EnsureSuccessStatusCode();
                
                var createdRelation = await response.Content.ReadFromJsonAsync<Relation>();
                return Ok(createdRelation);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating relation in FastAPI");
                return StatusCode(500, new { error = "Failed to add relation", detail = ex.Message });
            }
        }
    }
}
