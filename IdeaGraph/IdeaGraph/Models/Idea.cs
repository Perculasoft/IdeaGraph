using System.Text.Json.Serialization;

namespace IdeaGraph.Models
{
    public class Idea
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
        
        [JsonPropertyName("tags")]
        public List<string> Tags { get; set; } = new();
        
        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;
    }

    public class IdeaCreateRequest
    {
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;
        
        [JsonPropertyName("tags")]
        public List<string> Tags { get; set; } = new();
    }

    public class IdeaDetail : Idea
    {
        [JsonPropertyName("relations")]
        public List<Relation> Relations { get; set; } = new();
        
        [JsonPropertyName("impact_score")]
        public double ImpactScore { get; set; }
    }

    public class Relation
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("source_id")]
        public string SourceId { get; set; } = string.Empty;
        
        [JsonPropertyName("target_id")]
        public string TargetId { get; set; } = string.Empty;
        
        [JsonPropertyName("relation_type")]
        public string RelationType { get; set; } = string.Empty;
        
        [JsonPropertyName("weight")]
        public double Weight { get; set; }
    }

    public class RelationCreateRequest
    {
        [JsonPropertyName("source_id")]
        public string SourceId { get; set; } = string.Empty;
        
        [JsonPropertyName("target_id")]
        public string TargetId { get; set; } = string.Empty;
        
        [JsonPropertyName("relation_type")]
        public string RelationType { get; set; } = string.Empty;
        
        [JsonPropertyName("weight")]
        public double Weight { get; set; } = 1.0;
    }

    public class SimilarIdea : Idea
    {
        [JsonPropertyName("distance")]
        public double? Distance { get; set; }
    }

    public class HealthResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;
        
        [JsonPropertyName("collections")]
        public List<string> Collections { get; set; } = new();
    }
}
