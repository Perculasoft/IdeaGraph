using Microsoft.AspNetCore.Mvc;
using IdeaGraph.Models;
using IdeaGraph.Services;

namespace IdeaGraph.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class IdeasController : ControllerBase
    {
        private readonly IdeaService _ideaService;

        public IdeasController(IdeaService ideaService)
        {
            _ideaService = ideaService;
        }

        [HttpGet]
        public async Task<ActionResult<List<Idea>>> GetIdeas()
        {
            try
            {
                var ideas = await _ideaService.GetIdeasAsync();
                return Ok(ideas);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Idea>> CreateIdea([FromBody] IdeaCreateRequest request)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(request.Title))
                {
                    return BadRequest(new { error = "Title is required" });
                }

                var idea = await _ideaService.CreateIdeaAsync(request);
                if (idea == null)
                {
                    return StatusCode(500, new { error = "Failed to create idea" });
                }

                return CreatedAtAction(nameof(GetIdeas), new { id = idea.Id }, idea);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
