using Microsoft.AspNetCore.Identity;

namespace SymbioMatch.domain.Entities
{
    public class ApplicationUser : IdentityUser
    {
        public string Firtsname { get; set; }
        public string Lastname { get; set; }
        public Guid? CompanyId { get; set; }
        public Company Company { get; set; }
        public ICollection<UserMatch> UserMatches { get; set; } = [];
    }
}
