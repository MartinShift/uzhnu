namespace ArchKanban.Api.Models;

public class Member
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public Role Role { get; set; }

    public string Username { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public AccessLevel AccessLevel { get; set; } = AccessLevel.User;

    public ICollection<ProjectMember> ProjectMembers { get; set; } = new List<ProjectMember>();
}
