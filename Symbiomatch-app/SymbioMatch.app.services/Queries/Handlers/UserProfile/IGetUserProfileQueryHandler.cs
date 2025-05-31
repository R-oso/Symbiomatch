namespace SymbioMatch.app.services.Queries.Handlers.UserProfile
{
    public interface IGetUserProfileQueryHandler
    {
        Task<UserProfileResponse> HandleAsync(string userId);
    }
}
