using System.Text.Json.Serialization;

namespace IdeaGraph.Models
{
    public class Section
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
        
        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;
    }

    public class SectionCreateRequest
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
    }

    public class SectionUpdateRequest
    {
        [JsonPropertyName("name")]
        public string? Name { get; set; }
    }
}
