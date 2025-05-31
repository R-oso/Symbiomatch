using SymbioMatch.domain.Enums;

namespace SymbioMatch.app.Models
{
    public class MatchViewModel
    {
        public Guid Id { get; set; }
        public DateTime MatchedOn { get; set; }
        public MatchState State { get; set; }
        public ProductViewModel Product { get; set; }
        public CompanyViewModel Company { get; set; }
    }
}
