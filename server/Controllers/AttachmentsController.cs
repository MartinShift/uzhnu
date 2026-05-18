using ArchKanban.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ArchKanban.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/attachments")]
public class AttachmentsController : ControllerBase
{
    private readonly AppDbContext _db;

    public AttachmentsController(AppDbContext db) => _db = db;

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var attachment = await _db.Attachments.FindAsync(id);
        if (attachment is null) return NotFound();

        _db.Attachments.Remove(attachment);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
