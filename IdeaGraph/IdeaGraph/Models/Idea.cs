namespace IdeaGraph.Models
{
    public class Idea
    {
        public string Id { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
        public string CreatedAt { get; set; } = string.Empty;
    }

    public class IdeaCreateRequest
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
    }

    public class IdeaDetail : Idea
    {
        public List<Relation> Relations { get; set; } = new();
        public double ImpactScore { get; set; }
    }

    public class Relation
    {
        public string Id { get; set; } = string.Empty;
        public string SourceId { get; set; } = string.Empty;
        public string TargetId { get; set; } = string.Empty;
        public string RelationType { get; set; } = string.Empty;
        public double Weight { get; set; }
    }

    public class RelationCreateRequest
    {
        public string SourceId { get; set; } = string.Empty;
        public string TargetId { get; set; } = string.Empty;
        public string RelationType { get; set; } = string.Empty;
        public double Weight { get; set; } = 1.0;
    }

    public class SimilarIdea : Idea
    {
        public double? Distance { get; set; }
    }

    public class HealthResponse
    {
        public string Status { get; set; } = string.Empty;
        public List<string> Collections { get; set; } = new();
    }
}
