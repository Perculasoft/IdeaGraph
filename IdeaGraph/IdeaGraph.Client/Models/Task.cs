namespace IdeaGraph.Client.Models
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
        public string Id { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Repository { get; set; } = string.Empty;
        public string KiSuggestions { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
        public string Status { get; set; } = "New";
        public string CreatedAt { get; set; } = string.Empty;
        public string IdeaId { get; set; } = string.Empty;
    }

    public class TaskCreateRequest
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Repository { get; set; } = string.Empty;
        public string KiSuggestions { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new();
        public string Status { get; set; } = "New";
        public string IdeaId { get; set; } = string.Empty;
    }

    public class TaskUpdateRequest
    {
        public string? Title { get; set; }
        public string? Description { get; set; }
        public string? Repository { get; set; }
        public string? KiSuggestions { get; set; }
        public List<string>? Tags { get; set; }
        public string? Status { get; set; }
        public string? IdeaId { get; set; }
    }
}
