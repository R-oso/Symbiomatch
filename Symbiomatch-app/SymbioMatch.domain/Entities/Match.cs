using SymbioMatch.domain.Enums;

namespace SymbioMatch.domain.Entities
{
    public class Match
    {
        public Guid Id { get; set; }
        public DateTime MatchedOn { get; set; }
        public MatchState State { get; set; }
        public Guid ProductId { get; set; }
        public Product Product { get; set; }
        public ICollection<CompanyMatch> CompanyMatches { get; set; }
        public ICollection<UserMatch> UserMatches { get; set; }
    }
}
