using SymbioMatch.app.services.Queries.Handlers.Matches;

namespace SymbioMatch.app.services.Queries.Handlers.UserProfile
{
    public class UserProfileResponse
    {
        public string Firstname { get; set; }
        public string Lastname { get; set; }
        public string Email { get; set; }
        public string PhoneNumber { get; set; }
        public string CompanyName { get; set; }
        public List<MatchResponse> MatchHistory { get; set; }
    }
}
