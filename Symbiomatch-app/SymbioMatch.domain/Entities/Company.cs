namespace SymbioMatch.domain.Entities
{
    public class Company
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string NACECode { get; set; }
        public string Email { get; set; }
        public string Phonenumber { get; set; }
        // Navigation properties
        public Guid LocationId { get; set; }
        public Location Location { get; set; }
        public ICollection<CompanyMatch> CompanyMatches { get; set; } = [];
        public ICollection<ApplicationUser> Users { get; set; } = [];
        public List<Product> Products { get; set; } = [];
    }
}

// public List<Location> Locations { get; set; } If a company has multiple locations --> something to be added later
