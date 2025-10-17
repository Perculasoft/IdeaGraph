namespace IdeaGraph.Client.Models
{
    public enum IdeaStatus
    {
        New,
        Concept,
        Specification,
        Ready,
        Implemented,
        Discarded
    }

    public class Idea
    {
        public string Id { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
        public string CreatedAt { get; set; } = string.Empty;
        public string Status { get; set; } = "New";
        public string? SectionId { get; set; }
    }

    public class IdeaCreateRequest
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
        public string Status { get; set; } = "New";
        public string? SectionId { get; set; }
    }

    public class IdeaUpdateRequest
    {
        public string? Title { get; set; }
        public string? Description { get; set; }
        public List<string>? Tags { get; set; }
        public string? Status { get; set; }
        public string? SectionId { get; set; }
    }

    public class Relation
    {
        public string Id { get; set; } = string.Empty;
        public string SourceId { get; set; } = string.Empty;
        public string TargetId { get; set; } = string.Empty;
        public string RelationType { get; set; } = string.Empty;
        public double Weight { get; set; }
    }

    public class SimilarIdea : Idea
    {
        public double? Distance { get; set; }
    }
}
