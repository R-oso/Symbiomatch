using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using SymbioMatch.app.Models;
using SymbioMatch.app.services.Services;

namespace SymbioMatch.app.Controllers
{
    public class CompanyController(CompanyService companyService, IMapper mapper) : Controller
    {
        private readonly CompanyService _companyService = companyService;
        private readonly IMapper _mapper = mapper;
        public IActionResult Index()
        {
            return View();
        }

        // Get company by ID
        [HttpGet("company/{id}")]
        public async Task<IActionResult> Details(Guid id)
        {
            var companyDto = await _companyService.GetCompanyByIdAsync(id);
            if (companyDto == null)
            {
                return NotFound();
            }

            var viewModel = _mapper.Map<CompanyViewModel>(companyDto);
            return View(viewModel);
        }
    }
}
