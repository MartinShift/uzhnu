using System.Text.Json.Serialization;
using ArchKanban.Api.Auth;
using ArchKanban.Api.Data;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// In containerized hosts (Render, Fly.io, Heroku, ...) the bound port is
// passed via the PORT environment variable. Honor it if present.
var port = Environment.GetEnvironmentVariable("PORT");
if (!string.IsNullOrEmpty(port))
{
    builder.WebHost.UseUrls($"http://0.0.0.0:{port}");
}

builder.Services.AddControllers()
    .AddJsonOptions(opts =>
    {
        opts.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    });

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var provider = builder.Configuration["Database:Provider"] ?? "SqlServer";
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? (provider.Equals("Sqlite", StringComparison.OrdinalIgnoreCase)
        ? "Data Source=archkanban.db"
        : @"Server=(localdb)\MSSQLLocalDB;Database=ArchKanban;Trusted_Connection=True;TrustServerCertificate=True");

builder.Services.AddDbContext<AppDbContext>(opts =>
{
    if (provider.Equals("Sqlite", StringComparison.OrdinalIgnoreCase))
    {
        opts.UseSqlite(connectionString);
    }
    else
    {
        opts.UseSqlServer(connectionString);
    }
});

builder.Services.AddSingleton<TokenService>();

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(opts =>
    {
        opts.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = TokenService.GetKey(),
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1)
        };
    });

builder.Services.AddAuthorization();

const string CorsPolicy = "DevCors";
builder.Services.AddCors(opts =>
{
    opts.AddPolicy(CorsPolicy, p => p
        .WithOrigins("http://localhost:5173", "http://127.0.0.1:5173")
        .AllowAnyHeader()
        .AllowAnyMethod());
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DbSeeder.Seed(db);
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Serve the React build (wwwroot/) — only effective in containers/published output
app.UseDefaultFiles();
app.UseStaticFiles();

app.UseCors(CorsPolicy);
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", () => Results.Ok(new { status = "ok", time = DateTime.UtcNow }));
app.MapControllers();

// SPA fallback: any unmatched route returns index.html so React Router handles deep links.
// In development this won't match anything (no wwwroot/index.html) — Vite handles routing.
app.MapFallbackToFile("index.html");

app.Run();
