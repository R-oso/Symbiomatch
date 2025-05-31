using Microsoft.AspNetCore.Identity;
using SymbioMatch.app.services.DTOs.Auth;
using SymbioMatch.domain.Entities;

namespace SymbioMatch.app.services.Services
{
    public sealed class AuthService(
        UserManager<ApplicationUser> userManager,
        SignInManager<ApplicationUser> signInManager)
    {
        private readonly UserManager<ApplicationUser> _userManager = userManager;
        private readonly SignInManager<ApplicationUser> _signInManager = signInManager;

        // Register
        public async Task<IdentityResult> RegisterAsync(RegisterDto registerDto)
        {
            var user = new ApplicationUser
            {
                Firtsname = registerDto.Firstname,
                Lastname = registerDto.Lastname,
                UserName = registerDto.Firstname,
                Email = registerDto.Email,
                PhoneNumber = registerDto.Phonenumber,
                CompanyId = registerDto.CompanyId
            };

            return await _userManager.CreateAsync(user, registerDto.Password);
        }
    }
}