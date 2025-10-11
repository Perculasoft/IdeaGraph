using System.Net.Http.Json;
using IdeaGraph.Client.Models;

namespace IdeaGraph.Client.Services
{
    public class IdeaService
    {
        private readonly HttpClient _httpClient;

        public IdeaService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<Idea>> GetIdeasAsync()
        {
            try
            {
                var ideas = await _httpClient.GetFromJsonAsync<List<Idea>>("ideas");
                return ideas ?? new List<Idea>();
            }
            catch (Exception)
            {
                return new List<Idea>();
            }
        }

        public async Task<Idea?> CreateIdeaAsync(IdeaCreateRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("idea", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<Idea>();
            }
            catch (Exception)
            {
                return null;
            }
        }
    }
}
