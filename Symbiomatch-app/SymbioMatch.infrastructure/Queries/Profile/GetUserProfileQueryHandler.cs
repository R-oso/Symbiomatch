using Microsoft.EntityFrameworkCore;
using SymbioMatch.app.services.Queries.Handlers.Matches;
using SymbioMatch.app.services.Queries.Handlers.UserProfile;
using SymbioMatch.infrastructure.Database;

namespace SymbioMatch.infrastructure.Queries.Profile
{
    public class GetUserProfileQueryHandler(SymbioDbContext context) : IGetUserProfileQueryHandler
    {
        private readonly SymbioDbContext _context = context;

        public async Task<UserProfileResponse> HandleAsync(string userId)
        {
            var userProfile = await _context.Users
                .Where(u => u.Id == userId)
                .Select(u => new UserProfileResponse
                {
                    Firstname = u.Firtsname,
                    Lastname = u.Lastname,
                    Email = u.Email,
                    PhoneNumber = u.PhoneNumber,
                    CompanyName = u.Company.Name,
                    MatchHistory = u.UserMatches.Select(um => new MatchResponse
                    {
                        Id = um.Match.Id,
                        MatchedOn = um.Match.MatchedOn,
                        State = um.Match.State,
                        Product = um.Match.Product,
                        Company = um.User.Company
                    }).ToList()
                })
                .FirstOrDefaultAsync();

            if (userProfile == null)
            {
                throw new KeyNotFoundException($"User with ID '{userId}' not found.");
            }

            return userProfile;
        }
    }
}
