using System.Diagnostics;
using System.Net.Http.Json;
using IdeaGraph.Client.Models;

namespace IdeaGraph.Client.Services
{
    public class SectionService
    {
        private readonly HttpClient _httpClient;

        public SectionService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<Section>> GetSectionsAsync()
        {
            try
            {
                var sections = await _httpClient.GetFromJsonAsync<List<Section>>("api/sections");
                return sections ?? new List<Section>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<Section>();
            }
        }

        public async Task<Section?> GetSectionAsync(string id)
        {
            try
            {
                var section = await _httpClient.GetFromJsonAsync<Section>($"api/sections/{id}");
                return section;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<Section?> CreateSectionAsync(SectionCreateRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/sections", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<Section>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<Section?> UpdateSectionAsync(string id, SectionUpdateRequest request)
        {
            try
            {
                var response = await _httpClient.PutAsJsonAsync($"api/sections/{id}", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<Section>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<bool> DeleteSectionAsync(string id)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"api/sections/{id}");
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return false;
            }
        }
    }
}
