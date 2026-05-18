using ArchKanban.Api.Data;
using ArchKanban.Api.Dtos;
using ArchKanban.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace ArchKanban.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/members")]
public class MembersController : ControllerBase
{
    private readonly AppDbContext _db;

    public MembersController(AppDbContext db) => _db = db;

    [HttpGet]
    public async Task<ActionResult<IEnumerable<MemberDto>>> GetAll()
    {
        var members = await _db.Members
            .OrderBy(m => m.Name)
            .Select(m => new MemberDto(m.Id, m.Name, m.Role, m.Username, m.AccessLevel))
            .ToListAsync();
        return Ok(members);
    }

    [HttpPost]
    [Authorize(Roles = "Admin,Manager")]
    public async Task<ActionResult<MemberDto>> Create([FromBody] CreateMemberRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Name))
            return BadRequest("Name is required.");
        if (string.IsNullOrWhiteSpace(req.Username))
            return BadRequest("Username is required.");
        if (string.IsNullOrWhiteSpace(req.Password) || req.Password.Length < 4)
            return BadRequest("Password must be at least 4 characters.");

        var username = req.Username.Trim();
        var exists = await _db.Members.AnyAsync(m => m.Username == username);
        if (exists)
            return Conflict(new { message = "Username already taken." });

        var member = new Member
        {
            Name = req.Name.Trim(),
            Role = req.Role,
            Username = username,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.Password),
            AccessLevel = req.AccessLevel
        };
        _db.Members.Add(member);
        await _db.SaveChangesAsync();

        return Ok(new MemberDto(member.Id, member.Name, member.Role, member.Username, member.AccessLevel));
    }

    [HttpDelete("{id:int}")]
    [Authorize(Roles = "Admin,Manager")]
    public async Task<IActionResult> Delete(int id)
    {
        var member = await _db.Members.FindAsync(id);
        if (member is null) return NotFound();

        _db.Members.Remove(member);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
