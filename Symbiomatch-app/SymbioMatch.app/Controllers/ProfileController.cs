using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using SymbioMatch.app.Models;
using SymbioMatch.app.services.Queries.Handlers.UserProfile;

namespace SymbioMatch.app.Controllers
{
    public class ProfileController(IGetUserProfileQueryHandler getUserProfileQueryHandler, IMapper mapper) : Controller
    {
        private readonly IGetUserProfileQueryHandler _getUserProfileQueryHandler = getUserProfileQueryHandler;
        private readonly IMapper _mapper = mapper;

        [HttpGet("profile/{userId}")]
        public async Task<IActionResult> Details(string userId)
        {
            var profileResponse = await _getUserProfileQueryHandler.HandleAsync(userId);
            if (profileResponse == null)
            {
                return NotFound();
            }

            var viewModel = _mapper.Map<ProfileViewModel>(profileResponse);
            return View(viewModel);
        }
    }
}
