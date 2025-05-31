using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using SymbioMatch.domain.Entities;

namespace SymbioMatch.infrastructure.Database
{
    public class SymbioDbContext : IdentityDbContext<ApplicationUser>
    {
        public SymbioDbContext(DbContextOptions<SymbioDbContext> options) : base(options)
        {
        }

        public DbSet<Company> Companies { get; set; }
        public DbSet<Location> Locations { get; set; }
        public DbSet<Material> Materials { get; set; }
        public DbSet<Match> Matches { get; set; }
        public DbSet<Product> Products { get; set; }
        public DbSet<CompanyMatch> CompanyMatches { get; set; }
        public DbSet<UserMatch> UserMatches { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configuring Company Entity
            modelBuilder.Entity<Company>(entity =>
            {
                entity.HasKey(c => c.Id);

                entity.Property(c => c.Id)
                      .ValueGeneratedOnAdd()
                      .HasDefaultValueSql("UUID()");

                entity.Property(c => c.Name)
                      .IsRequired()
                      .HasMaxLength(100);

                // Company - Product (One-to-Many)
                entity.HasMany(c => c.Products)
                      .WithOne(p => p.Company)
                      .HasForeignKey(p => p.CompanyId)
                      .OnDelete(DeleteBehavior.Cascade);

                // Company - ApplicationUser (One-to-Many)
                entity.HasMany(c => c.Users)
                      .WithOne(u => u.Company)
                      .HasForeignKey(u => u.CompanyId)
                      .OnDelete(DeleteBehavior.SetNull);

                entity.HasOne(c => c.Location)
                      .WithOne()
                      .HasForeignKey<Company>(c => c.LocationId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // Configuring Material Entity
            modelBuilder.Entity<Material>(entity =>
            {
                entity.HasKey(m => m.Id);

                entity.Property(m => m.Id)
                      .ValueGeneratedOnAdd()
                      .HasDefaultValueSql("UUID()");

                entity.Property(m => m.Name)
                      .IsRequired()
                      .HasMaxLength(100);

                entity.Property(m => m.Description)
                      .HasMaxLength(500);

                entity.Property(m => m.Category)
                      .HasMaxLength(100);

                entity.Property(m => m.AvailableQuantity)
                      .IsRequired();

                entity.Property(m => m.UnitOfMeasure)
                      .IsRequired();

                entity.Property(m => m.ExpiresAt)
                      .IsRequired();

                // Material - Product (Many-to-One)
                entity.HasOne(m => m.Product)
                      .WithMany(p => p.Materials)
                      .HasForeignKey(m => m.ProductId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configuring Product Entity
            modelBuilder.Entity<Product>(entity =>
            {
                entity.HasKey(p => p.Id);

                entity.Property(p => p.Id)
                      .ValueGeneratedOnAdd()
                      .HasDefaultValueSql("UUID()");

                entity.Property(p => p.Name)
                      .IsRequired()
                      .HasMaxLength(100);

                entity.Property(p => p.CreatedOn)
                      .IsRequired();

                // Product - Material (One-to-Many)
                entity.HasMany(p => p.Materials)
                      .WithOne(m => m.Product)
                      .HasForeignKey(m => m.ProductId)
                      .OnDelete(DeleteBehavior.Restrict);

                // Product - Company (Many-to-One)
                entity.HasOne(p => p.Company)
                      .WithMany(c => c.Products)
                      .HasForeignKey(p => p.CompanyId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configuring Match Entity
            modelBuilder.Entity<Match>(entity =>
            {
                entity.HasKey(m => m.Id);

                entity.Property(m => m.Id)
                      .ValueGeneratedOnAdd()
                      .HasDefaultValueSql("UUID()");

                entity.Property(m => m.MatchedOn)
                      .IsRequired();

                entity.Property(m => m.State)
                      .IsRequired();
            });

            modelBuilder.Entity<ApplicationUser>(entity =>
            {
                entity.HasOne(u => u.Company)
                      .WithMany(c => c.Users)
                      .HasForeignKey(u => u.CompanyId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // Match - Company (Many-to-Many through CompanyMatch)
            modelBuilder.Entity<CompanyMatch>(entity =>
            {
                entity.HasKey(cm => new { cm.CompanyId, cm.MatchId });

                entity.HasOne(cm => cm.Company)
                      .WithMany(c => c.CompanyMatches)
                      .HasForeignKey(cm => cm.CompanyId)
                      .OnDelete(DeleteBehavior.Cascade);

                entity.HasOne(cm => cm.Match)
                      .WithMany(m => m.CompanyMatches)
                      .HasForeignKey(cm => cm.MatchId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // Match - ApplicationUser (Many-to-Many through UserMatch)
            modelBuilder.Entity<UserMatch>(entity =>
            {
                entity.HasKey(um => new { um.UserId, um.MatchId });

                entity.HasOne(um => um.User)
                      .WithMany(u => u.UserMatches)
                      .HasForeignKey(um => um.UserId)
                      .OnDelete(DeleteBehavior.Cascade);

                entity.HasOne(um => um.Match)
                      .WithMany(m => m.UserMatches)
                      .HasForeignKey(um => um.MatchId)
                      .OnDelete(DeleteBehavior.Cascade);
            });
        }
    }
}
