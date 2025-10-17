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
                var response = await _httpClient.GetAsync($"api/similar/{ideaId}?k={k}");
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Error fetching similar ideas: {response.StatusCode} - {errorContent}");
                    Debug.WriteLine($"Error fetching similar ideas: {response.StatusCode} - {errorContent}");
                    return new List<SimilarIdea>();
                }
                
                var similarIdeas = await response.Content.ReadFromJsonAsync<List<SimilarIdea>>();
                return similarIdeas ?? new List<SimilarIdea>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception fetching similar ideas: {ex}");
                Debug.WriteLine($"Exception fetching similar ideas: {ex}");
                return new List<SimilarIdea>();
            }
        }
    }
}
