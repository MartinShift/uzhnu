using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ArchKanban.Api.Models;
using Microsoft.IdentityModel.Tokens;

namespace ArchKanban.Api.Auth;

public class TokenService
{
    public const string SecretKey =
        "ArchKanbanDemoSecret_ThisIsLongEnough_ChangeForRealUsage_OnlyADemo!!"; // demo only

    public static SymmetricSecurityKey GetKey() =>
        new(Encoding.UTF8.GetBytes(SecretKey));

    public string Issue(Member member)
    {
        var handler = new JwtSecurityTokenHandler();
        var creds = new SigningCredentials(GetKey(), SecurityAlgorithms.HmacSha256);

        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, member.Id.ToString()),
            new(ClaimTypes.NameIdentifier, member.Id.ToString()),
            new(ClaimTypes.Name, member.Name),
            new(ClaimTypes.Role, member.AccessLevel.ToString())
        };

        var token = new JwtSecurityToken(
            claims: claims,
            expires: DateTime.UtcNow.AddHours(8),
            signingCredentials: creds
        );

        return handler.WriteToken(token);
    }
}
