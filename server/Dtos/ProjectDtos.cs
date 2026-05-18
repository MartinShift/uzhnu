using ArchKanban.Api.Models;

namespace ArchKanban.Api.Dtos;

public record MemberDto(int Id, string Name, Role Role, string Username, AccessLevel AccessLevel);

public record LoginRequest(string Username, string Password);

public record LoginResponse(string Token, MemberDto User);

public record AttachmentDto(int Id, string Label, string Url);

public record CommentDto(int Id, string Author, string Text, DateTime CreatedAt);

public record ProjectDto(
    int Id,
    string Title,
    string ClientName,
    string? Description,
    Stage Stage,
    Priority Priority,
    int Position,
    DateTime? DueDate,
    DateTime CreatedAt,
    IEnumerable<MemberDto> Members,
    IEnumerable<AttachmentDto> Attachments,
    IEnumerable<CommentDto> Comments
);

public class CreateProjectRequest
{
    public string Title { get; set; } = string.Empty;
    public string ClientName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Stage Stage { get; set; } = Stage.Sketch;
    public Priority Priority { get; set; } = Priority.Medium;
    public DateTime? DueDate { get; set; }
}

public class UpdateProjectRequest
{
    public string Title { get; set; } = string.Empty;
    public string ClientName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Priority Priority { get; set; } = Priority.Medium;
    public DateTime? DueDate { get; set; }
}

public class MoveProjectRequest
{
    public Stage Stage { get; set; }
    public int Position { get; set; }
}

public class CreateMemberRequest
{
    public string Name { get; set; } = string.Empty;
    public Role Role { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public AccessLevel AccessLevel { get; set; } = AccessLevel.User;
}

public class CreateAttachmentRequest
{
    public string Label { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
}

public class CreateCommentRequest
{
    public string Text { get; set; } = string.Empty;
}
