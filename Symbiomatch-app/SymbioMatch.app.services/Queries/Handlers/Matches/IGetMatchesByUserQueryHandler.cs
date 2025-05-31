namespace SymbioMatch.app.services.Queries.Handlers.Matches;
public interface IGetMatchesByUserQueryHandler
{
    Task<List<MatchResponse>> HandleAsync(Guid userId);
}
