namespace SymbioMatch.domain.Entities
{
    public class CompanyMatch
    {
        public Guid CompanyId { get; set; }
        public Company Company { get; set; }

        public Guid MatchId { get; set; }
        public Match Match { get; set; }
    }
}
