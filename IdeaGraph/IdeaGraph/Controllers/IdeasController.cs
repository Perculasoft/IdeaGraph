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
                var response = await _httpClient.GetFromJsonAsync<List<Idea>>($"ideas");
                return Ok(response);
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

       
    }
}
