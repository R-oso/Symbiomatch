using SymbioMatch.domain.Entities;
using SymbioMatch.domain.Enums;

namespace SymbioMatch.app.services.Queries.Handlers.Matches;

public class MatchResponse
{
    public Guid Id { get; set; }
    public DateTime MatchedOn { get; set; }
    public MatchState State { get; set; }
    public domain.Entities.Product Product { get; set; }
    public Company Company { get; set; }
}
