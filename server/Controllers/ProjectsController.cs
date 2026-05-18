using System.Security.Claims;
using ArchKanban.Api.Data;
using ArchKanban.Api.Dtos;
using ArchKanban.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace ArchKanban.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/projects")]
public class ProjectsController : ControllerBase
{
    private readonly AppDbContext _db;

    public ProjectsController(AppDbContext db) => _db = db;

    [HttpGet]
    [AllowAnonymous]
    public async Task<ActionResult<IEnumerable<ProjectDto>>> GetAll()
    {
        var projects = await _db.Projects
            .Include(p => p.Attachments)
            .Include(p => p.Comments)
            .Include(p => p.ProjectMembers)
                .ThenInclude(pm => pm.Member)
            .OrderBy(p => p.Stage).ThenBy(p => p.Position)
            .ToListAsync();

        return Ok(projects.Select(ToDto));
    }

    [HttpGet("{id:int}")]
    [AllowAnonymous]
    public async Task<ActionResult<ProjectDto>> GetById(int id)
    {
        var project = await LoadAsync(id);
        return project is null ? NotFound() : Ok(ToDto(project));
    }

    [HttpPost]
    public async Task<ActionResult<ProjectDto>> Create([FromBody] CreateProjectRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Title))
        {
            return BadRequest("Title is required.");
        }

        var maxPos = await _db.Projects
            .Where(p => p.Stage == req.Stage)
            .Select(p => (int?)p.Position)
            .MaxAsync() ?? -1;

        var project = new Project
        {
            Title = req.Title.Trim(),
            ClientName = req.ClientName?.Trim() ?? string.Empty,
            Description = req.Description,
            Stage = req.Stage,
            Priority = req.Priority,
            Position = maxPos + 1,
            DueDate = req.DueDate,
            CreatedAt = DateTime.UtcNow
        };

        _db.Projects.Add(project);
        await _db.SaveChangesAsync();

        var loaded = await LoadAsync(project.Id);
        return CreatedAtAction(nameof(GetById), new { id = project.Id }, ToDto(loaded!));
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<ProjectDto>> Update(int id, [FromBody] UpdateProjectRequest req)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound();

        if (string.IsNullOrWhiteSpace(req.Title))
        {
            return BadRequest("Title is required.");
        }

        project.Title = req.Title.Trim();
        project.ClientName = req.ClientName?.Trim() ?? string.Empty;
        project.Description = req.Description;
        project.Priority = req.Priority;
        project.DueDate = req.DueDate;

        await _db.SaveChangesAsync();

        var loaded = await LoadAsync(id);
        return Ok(ToDto(loaded!));
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound();

        _db.Projects.Remove(project);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPatch("{id:int}/move")]
    public async Task<IActionResult> Move(int id, [FromBody] MoveProjectRequest req)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound();

        // Re-sequence positions inside the source column (excluding moved card)
        var sourceStage = project.Stage;
        var targetStage = req.Stage;
        var targetPos = Math.Max(0, req.Position);

        project.Stage = targetStage;
        // temporarily push out of range so it doesn't interfere with re-sequencing
        project.Position = int.MaxValue;
        await _db.SaveChangesAsync();

        if (sourceStage != targetStage)
        {
            var sourceCards = await _db.Projects
                .Where(p => p.Stage == sourceStage && p.Id != project.Id)
                .OrderBy(p => p.Position)
                .ToListAsync();
            for (var i = 0; i < sourceCards.Count; i++)
            {
                sourceCards[i].Position = i;
            }
        }

        var targetCards = await _db.Projects
            .Where(p => p.Stage == targetStage && p.Id != project.Id)
            .OrderBy(p => p.Position)
            .ToListAsync();

        targetPos = Math.Min(targetPos, targetCards.Count);
        targetCards.Insert(targetPos, project);
        for (var i = 0; i < targetCards.Count; i++)
        {
            targetCards[i].Position = i;
        }

        await _db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPost("{id:int}/members/{memberId:int}")]
    public async Task<IActionResult> AssignMember(int id, int memberId)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound("Project not found.");

        var member = await _db.Members.FindAsync(memberId);
        if (member is null) return NotFound("Member not found.");

        var exists = await _db.ProjectMembers
            .AnyAsync(pm => pm.ProjectId == id && pm.MemberId == memberId);
        if (exists) return NoContent();

        _db.ProjectMembers.Add(new ProjectMember { ProjectId = id, MemberId = memberId });
        await _db.SaveChangesAsync();
        return NoContent();
    }

    [HttpDelete("{id:int}/members/{memberId:int}")]
    public async Task<IActionResult> UnassignMember(int id, int memberId)
    {
        var link = await _db.ProjectMembers
            .FirstOrDefaultAsync(pm => pm.ProjectId == id && pm.MemberId == memberId);
        if (link is null) return NotFound();

        _db.ProjectMembers.Remove(link);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPost("{id:int}/attachments")]
    public async Task<ActionResult<AttachmentDto>> AddAttachment(int id, [FromBody] CreateAttachmentRequest req)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound();

        if (string.IsNullOrWhiteSpace(req.Label) || string.IsNullOrWhiteSpace(req.Url))
        {
            return BadRequest("Label and Url are required.");
        }

        var attachment = new Attachment
        {
            ProjectId = id,
            Label = req.Label.Trim(),
            Url = req.Url.Trim()
        };
        _db.Attachments.Add(attachment);
        await _db.SaveChangesAsync();

        return Ok(new AttachmentDto(attachment.Id, attachment.Label, attachment.Url));
    }

    [HttpPost("{id:int}/comments")]
    public async Task<ActionResult<CommentDto>> AddComment(int id, [FromBody] CreateCommentRequest req)
    {
        var project = await _db.Projects.FindAsync(id);
        if (project is null) return NotFound();

        if (string.IsNullOrWhiteSpace(req.Text))
        {
            return BadRequest("Text is required.");
        }

        var author = User.FindFirstValue(ClaimTypes.Name) ?? "Unknown";

        var comment = new Comment
        {
            ProjectId = id,
            Author = author,
            Text = req.Text.Trim(),
            CreatedAt = DateTime.UtcNow
        };
        _db.Comments.Add(comment);
        await _db.SaveChangesAsync();

        return Ok(new CommentDto(comment.Id, comment.Author, comment.Text, comment.CreatedAt));
    }

    [HttpDelete("comments/{commentId:int}")]
    public async Task<IActionResult> DeleteComment(int commentId)
    {
        var comment = await _db.Comments.FindAsync(commentId);
        if (comment is null) return NotFound();

        _db.Comments.Remove(comment);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    private Task<Project?> LoadAsync(int id) => _db.Projects
        .Include(p => p.Attachments)
        .Include(p => p.Comments)
        .Include(p => p.ProjectMembers)
            .ThenInclude(pm => pm.Member)
        .FirstOrDefaultAsync(p => p.Id == id);

    private static ProjectDto ToDto(Project p) => new(
        p.Id,
        p.Title,
        p.ClientName,
        p.Description,
        p.Stage,
        p.Priority,
        p.Position,
        p.DueDate,
        p.CreatedAt,
        p.ProjectMembers.Select(pm => new MemberDto(pm.Member.Id, pm.Member.Name, pm.Member.Role, pm.Member.Username, pm.Member.AccessLevel)),
        p.Attachments.Select(a => new AttachmentDto(a.Id, a.Label, a.Url)),
        p.Comments.OrderBy(c => c.CreatedAt).Select(c => new CommentDto(c.Id, c.Author, c.Text, c.CreatedAt))
    );
}
