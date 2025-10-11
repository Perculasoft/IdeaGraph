using System.Diagnostics;
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
                var ideas = await _httpClient.GetFromJsonAsync<List<Idea>>("api/ideas");
                return ideas ?? new List<Idea>();
            }
            catch (Exception ex)
            {
                Debug.WriteLine(ex.ToString());
                return new List<Idea>();
            }
        }

        public async Task<Idea?> CreateIdeaAsync(IdeaCreateRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/ideas", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<Idea>();
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<Idea?> UpdateIdeaAsync(string id, IdeaUpdateRequest request)
        {
            try
            {
                var response = await _httpClient.PutAsJsonAsync($"api/ideas/{id}", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<Idea>();
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<bool> DeleteIdeaAsync(string id)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"api/ideas/{id}");
                return response.IsSuccessStatusCode;
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
