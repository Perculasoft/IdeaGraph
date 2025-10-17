using System.Diagnostics;
using System.Net.Http.Json;
using IdeaGraph.Client.Models;

namespace IdeaGraph.Client.Services
{
    public class SimilarService
    {
        private readonly HttpClient _httpClient;

        public SimilarService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<SimilarIdea>> GetSimilarIdeasAsync(string ideaId, int k = 5)
        {
            try
            {
                var similarIdeas = await _httpClient.GetFromJsonAsync<List<SimilarIdea>>($"api/similar/{ideaId}?k={k}");
                return similarIdeas ?? new List<SimilarIdea>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<SimilarIdea>();
            }
        }
    }
}
