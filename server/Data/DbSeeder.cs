using ArchKanban.Api.Models;

namespace ArchKanban.Api.Data;

public static class DbSeeder
{
    public static void Seed(AppDbContext db)
    {
        if (db.Members.Any() || db.Projects.Any())
        {
            return;
        }

        string Hash(string pw) => BCrypt.Net.BCrypt.HashPassword(pw);

        var members = new[]
        {
            new Member { Name = "Адміністратор",  Role = Role.Architect,   Username = "admin",  PasswordHash = Hash("admin"), AccessLevel = AccessLevel.Admin },
            new Member { Name = "Олена Коваль",   Role = Role.Architect,   Username = "olena",  PasswordHash = Hash("pass"),  AccessLevel = AccessLevel.Manager },
            new Member { Name = "Тарас Дзюба",    Role = Role.Architect,   Username = "taras",  PasswordHash = Hash("pass"),  AccessLevel = AccessLevel.User },
            new Member { Name = "Софія Мельник",  Role = Role.Designer,    Username = "sofia",  PasswordHash = Hash("pass"),  AccessLevel = AccessLevel.User },
            new Member { Name = "Андрій Петренко",Role = Role.Constructor, Username = "andriy", PasswordHash = Hash("pass"),  AccessLevel = AccessLevel.User },
            new Member { Name = "Марія Бойко",    Role = Role.Designer,    Username = "maria",  PasswordHash = Hash("pass"),  AccessLevel = AccessLevel.User }
        };
        db.Members.AddRange(members);
        db.SaveChanges();

        var p1 = new Project
        {
            Title = "Вілла в Ужгороді",
            ClientName = "Родина Гриценків",
            Description = "Двоповерхова вілла з басейном на схилі",
            Stage = Stage.Sketch,
            Priority = Priority.High,
            Position = 0,
            DueDate = DateTime.UtcNow.AddDays(30)
        };
        var p2 = new Project
        {
            Title = "Котедж на Закарпатті",
            ClientName = "ТОВ \"Карпатські Оселі\"",
            Description = "Дерев'яний котедж у стилі шале",
            Stage = Stage.ClientApproval,
            Priority = Priority.Medium,
            Position = 0,
            DueDate = DateTime.UtcNow.AddDays(14)
        };
        var p3 = new Project
        {
            Title = "Офісний центр \"Меридіан\"",
            ClientName = "Меридіан Інвест",
            Description = "5-поверховий офісний центр класу B+",
            Stage = Stage.Drawings,
            Priority = Priority.Urgent,
            Position = 0,
            DueDate = DateTime.UtcNow.AddDays(60)
        };
        var p4 = new Project
        {
            Title = "Реконструкція кав'ярні",
            ClientName = "Coffee Lab",
            Description = "Інтер'єр та фасад невеликої кав'ярні в центрі",
            Stage = Stage.Done,
            Priority = Priority.Low,
            Position = 0,
            DueDate = DateTime.UtcNow.AddDays(-5)
        };

        db.Projects.AddRange(p1, p2, p3, p4);
        db.SaveChanges();

        // Indexes: 0=admin, 1=Olena, 2=Taras, 3=Sofia, 4=Andriy, 5=Maria
        db.ProjectMembers.AddRange(
            new ProjectMember { ProjectId = p1.Id, MemberId = members[1].Id }, // Olena on Villa
            new ProjectMember { ProjectId = p1.Id, MemberId = members[3].Id }, // Sofia on Villa
            new ProjectMember { ProjectId = p2.Id, MemberId = members[2].Id }, // Taras on Cottage
            new ProjectMember { ProjectId = p3.Id, MemberId = members[1].Id }, // Olena on Meridian
            new ProjectMember { ProjectId = p3.Id, MemberId = members[4].Id }, // Andriy on Meridian
            new ProjectMember { ProjectId = p4.Id, MemberId = members[5].Id }  // Maria on Cafe
        );

        db.Attachments.AddRange(
            new Attachment { ProjectId = p1.Id, Label = "Ескіз фасаду",        Url = "https://example.com/villa-facade.pdf" },
            new Attachment { ProjectId = p3.Id, Label = "Генеральний план",    Url = "https://example.com/meridian-plan.pdf" },
            new Attachment { ProjectId = p3.Id, Label = "Схема вентиляції",    Url = "https://example.com/meridian-hvac.pdf" }
        );

        db.Comments.AddRange(
            new Comment
            {
                ProjectId = p1.Id,
                Author = "Олена Коваль",
                Text = "Замовник хоче ще раз переглянути планування першого поверху.",
                CreatedAt = DateTime.UtcNow.AddDays(-2)
            },
            new Comment
            {
                ProjectId = p1.Id,
                Author = "Софія Мельник",
                Text = "Підготувала три варіанти фасадних матеріалів — обговоримо завтра.",
                CreatedAt = DateTime.UtcNow.AddHours(-5)
            },
            new Comment
            {
                ProjectId = p3.Id,
                Author = "Андрій Петренко",
                Text = "Розрахунок навантажень готовий, передаю на креслення.",
                CreatedAt = DateTime.UtcNow.AddHours(-1)
            }
        );

        db.SaveChanges();
    }
}
