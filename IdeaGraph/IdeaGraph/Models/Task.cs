using System.Text.Json.Serialization;

namespace IdeaGraph.Models
{
    public enum TaskStatus
    {
        New,
        InWork,
        Review,
        Ready,
        Closed
    }

    public class IdeaTask
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
        
        [JsonPropertyName("repository")]
        public string Repository { get; set; } = string.Empty;
        
        [JsonPropertyName("ki_suggestions")]
        public string KiSuggestions { get; set; } = string.Empty;
        
        [JsonPropertyName("tags")]
        public List<string> Tags { get; set; } = new();
        
        [JsonPropertyName("status")]
        public string Status { get; set; } = "New";
        
        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;
        
        [JsonPropertyName("idea_id")]
        public string IdeaId { get; set; } = string.Empty;
    }

    public class TaskCreateRequest
    {
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
        
        [JsonPropertyName("repository")]
        public string Repository { get; set; } = string.Empty;
        
        [JsonPropertyName("ki_suggestions")]
        public string KiSuggestions { get; set; } = string.Empty;
        
        [JsonPropertyName("tags")]
        public List<string> Tags { get; set; } = new();
        
        [JsonPropertyName("status")]
        public string Status { get; set; } = "New";
        
        [JsonPropertyName("idea_id")]
        public string IdeaId { get; set; } = string.Empty;
    }

    public class TaskUpdateRequest
    {
        [JsonPropertyName("title")]
        public string? Title { get; set; }
        
        [JsonPropertyName("description")]
        public string? Description { get; set; }
        
        [JsonPropertyName("repository")]
        public string? Repository { get; set; }
        
        [JsonPropertyName("ki_suggestions")]
        public string? KiSuggestions { get; set; }
        
        [JsonPropertyName("tags")]
        public List<string>? Tags { get; set; }
        
        [JsonPropertyName("status")]
        public string? Status { get; set; }
        
        [JsonPropertyName("idea_id")]
        public string? IdeaId { get; set; }
    }
}
