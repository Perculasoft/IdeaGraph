using System.Diagnostics;
using System.Net.Http.Json;
using IdeaGraph.Client.Models;

namespace IdeaGraph.Client.Services
{
    public class RelationService
    {
        private readonly HttpClient _httpClient;

        public RelationService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<Relation>> GetRelationsAsync(string ideaId)
        {
            try
            {
                var relations = await _httpClient.GetFromJsonAsync<List<Relation>>($"api/relations/{ideaId}");
                return relations ?? new List<Relation>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<Relation>();
            }
        }
    }
}
