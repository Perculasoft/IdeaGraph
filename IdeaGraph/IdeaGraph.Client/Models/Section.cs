namespace IdeaGraph.Client.Models
{
    public class Section
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string CreatedAt { get; set; } = string.Empty;
    }

    public class SectionCreateRequest
    {
        public string Name { get; set; } = string.Empty;
    }

    public class SectionUpdateRequest
    {
        public string? Name { get; set; }
    }
}
