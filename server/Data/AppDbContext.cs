using ArchKanban.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace ArchKanban.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Project> Projects => Set<Project>();
    public DbSet<Member> Members => Set<Member>();
    public DbSet<ProjectMember> ProjectMembers => Set<ProjectMember>();
    public DbSet<Attachment> Attachments => Set<Attachment>();
    public DbSet<Comment> Comments => Set<Comment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ProjectMember>()
            .HasKey(pm => new { pm.ProjectId, pm.MemberId });

        modelBuilder.Entity<ProjectMember>()
            .HasOne(pm => pm.Project)
            .WithMany(p => p.ProjectMembers)
            .HasForeignKey(pm => pm.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<ProjectMember>()
            .HasOne(pm => pm.Member)
            .WithMany(m => m.ProjectMembers)
            .HasForeignKey(pm => pm.MemberId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Attachment>()
            .HasOne(a => a.Project)
            .WithMany(p => p.Attachments)
            .HasForeignKey(a => a.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Project>()
            .Property(p => p.Title).IsRequired().HasMaxLength(200);
        modelBuilder.Entity<Project>()
            .Property(p => p.ClientName).HasMaxLength(200);

        modelBuilder.Entity<Member>()
            .Property(m => m.Name).IsRequired().HasMaxLength(200);
        modelBuilder.Entity<Member>()
            .Property(m => m.Username).IsRequired().HasMaxLength(100);
        modelBuilder.Entity<Member>()
            .Property(m => m.PasswordHash).IsRequired().HasMaxLength(200);
        modelBuilder.Entity<Member>()
            .HasIndex(m => m.Username).IsUnique();

        modelBuilder.Entity<Attachment>()
            .Property(a => a.Label).IsRequired().HasMaxLength(200);
        modelBuilder.Entity<Attachment>()
            .Property(a => a.Url).IsRequired().HasMaxLength(1000);

        modelBuilder.Entity<Comment>()
            .HasOne(c => c.Project)
            .WithMany(p => p.Comments)
            .HasForeignKey(c => c.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);
        modelBuilder.Entity<Comment>()
            .Property(c => c.Author).IsRequired().HasMaxLength(200);
        modelBuilder.Entity<Comment>()
            .Property(c => c.Text).IsRequired().HasMaxLength(4000);
    }
}
