namespace ArchKanban.Api.Models;

public class Attachment
{
    public int Id { get; set; }
    public int ProjectId { get; set; }
    public Project Project { get; set; } = null!;
    public string Label { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
}
