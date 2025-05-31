using SymbioMatch.app.services.DTOs;
using SymbioMatch.domain.Entities;
using SymbioMatch.domain.Repositories;

namespace SymbioMatch.app.services.Services
{
    public sealed class CompanyService(ICompanyRepository companyRepository)
    {
        private readonly ICompanyRepository _companyRepository = companyRepository;

        public async Task<Guid> CreateAsync(CompanyDto companyDto)
        {
            var company = new Company
            {
                Id = Guid.NewGuid(),
                Name = companyDto.Name,
            };

            var companyId = await _companyRepository.InsertAsync(company);

            return companyId;
        }

        public async Task<List<CompanyDto>> GetCompaniesAsync()
        {
            var companies = await _companyRepository.GetAllAsync();
            return companies.Select(c => new CompanyDto
            {
                Id = c.Id,
                Name = c.Name,
            }).ToList();
        }

        public async Task<CompanyDto> GetCompanyByIdAsync(Guid id)
        {
            var company = await _companyRepository.GetByIdAsync(id);
            return new CompanyDto
            {
                Id = company.Id,
                Name = company.Name,
            };
        }
    }
}
