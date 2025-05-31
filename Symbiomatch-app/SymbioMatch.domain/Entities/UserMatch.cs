namespace SymbioMatch.domain.Entities
{
    public class UserMatch
    {
        public string UserId { get; set; }
        public ApplicationUser User { get; set; }
        public Guid MatchId { get; set; }
        public Match Match { get; set; }
    }
}
