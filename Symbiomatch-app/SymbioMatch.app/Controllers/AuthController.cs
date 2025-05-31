using AutoMapper;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using SymbioMatch.app.Models;
using SymbioMatch.app.Models.Auth;
using SymbioMatch.app.services.DTOs;
using SymbioMatch.app.services.DTOs.Auth;
using SymbioMatch.app.services.Services;
using SymbioMatch.domain.Entities;

namespace SymbioMatch.app.Controllers
{
    public class AuthController(SignInManager<ApplicationUser> signInManager, UserManager<ApplicationUser> userManager,
        CompanyService companyService, AuthService authService,
        IMapper mapper) : Controller
    {
        private readonly SignInManager<ApplicationUser> _signInManager = signInManager;
        private readonly UserManager<ApplicationUser> _userManager = userManager;
        private readonly CompanyService _companyService = companyService;
        private readonly AuthService _authService = authService;
        private readonly IMapper _mapper = mapper;

        [HttpGet("login")]
        public IActionResult Login()
        {
            return View();
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(LoginViewModel model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);
            }
            var user = await _userManager.FindByEmailAsync(model.Email);
            if (user == null)
            {
                ModelState.AddModelError(string.Empty, "Account with this email does not exist.");
                return View(model);
            }

            // Attempt to sign in the user
            var result = await _signInManager.PasswordSignInAsync(user, model.Password, isPersistent: false, lockoutOnFailure: false);

            if (result.Succeeded)
            {
                return RedirectToAction("Index", "Home");
            }
            else
            {
                ModelState.AddModelError(string.Empty, "Incorrect password.");
            }
            return View(model);
        }

        [HttpGet("register")]
        public async Task<IActionResult> Register()
        {
            var companies = await _companyService.GetCompaniesAsync();
            ViewBag.Companies = new SelectList(companies, "Id", "Name");

            var registerViewModel = new RegisterViewModel
            {
                NewCompany = new CompanyViewModel()
            };
            return View(registerViewModel);
        }


        [HttpPost("register")]
        public async Task<IActionResult> Register(RegisterViewModel model)
        {
            if (!ModelState.IsValid)
            {
                // Return a JSON response with validation errors
                var companies = await _companyService.GetCompaniesAsync();
                ViewBag.Companies = new SelectList(companies, "Id", "Name");

                var errors = ModelState.Values.SelectMany(v => v.Errors)
                                               .Select(e => e.ErrorMessage).ToList();
                return Json(new { success = false, errors });
            }

            if (!string.IsNullOrEmpty(model.NewCompany?.Name))
            {
                model.CompanyId = await CreateNewCompanyAsync(model.NewCompany);
            }

            var registerDto = _mapper.Map<RegisterDto>(model);
            var result = await _authService.RegisterAsync(registerDto);

            if (result.Succeeded)
            {
                var user = await _userManager.FindByEmailAsync(model.Email);
                await _signInManager.SignInAsync(user, isPersistent: false);

                // Return a JSON response with success and the URL to redirect
                return Json(new { success = true, redirectUrl = Url.Action("Index", "Home") });
            }

            // If registration fails, return an error response
            return Json(new { success = false, errors = new List<string> { "Registration failed. Please try again." } });
        }


        [HttpPost]
        public async Task<IActionResult> Logout()
        {
            // Sign out the user
            await _signInManager.SignOutAsync();
            return RedirectToAction("Login", "Auth");
        }

        private async Task<Guid> CreateNewCompanyAsync(CompanyViewModel newCompany)
        {
            var newCompanyDto = _mapper.Map<CompanyDto>(newCompany);
            return await _companyService.CreateAsync(newCompanyDto);
        }

    }
}
