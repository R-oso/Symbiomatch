using Microsoft.EntityFrameworkCore;
using SymbioMatch.domain.Entities;
using SymbioMatch.domain.Repositories;
using SymbioMatch.infrastructure.Database;

namespace SymbioMatch.infrastructure.Repositories
{
    public sealed class CompanyRepository(SymbioDbContext dbContext) : ICompanyRepository
    {
        private readonly SymbioDbContext _dbContext = dbContext;

        public async Task<List<Company>> GetAllAsync()
        {
            return await _dbContext.Companies.ToListAsync();
        }

        public async Task<Guid> InsertAsync(Company Company)
        {
            _dbContext.Companies.Add(Company);

            await _dbContext.SaveChangesAsync();

            return Company.Id;
        }

        public async Task<Company?> GetByIdAsync(Guid id)
        {
            return await _dbContext.Companies.FirstOrDefaultAsync(a => a.Id == id);
        }

        public async Task UpdateAsync(Company Company)
        {
            _dbContext.Companies.Update(Company);

            await _dbContext.SaveChangesAsync();
        }
    }
}
