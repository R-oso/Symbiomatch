using SymbioMatch.domain.Entities;

namespace SymbioMatch.domain.Repositories
{
    public interface ICompanyRepository
    {
        Task<List<Company>> GetAllAsync();
        Task<Guid> InsertAsync(Company Company);
        Task<Company?> GetByIdAsync(Guid id);
        Task UpdateAsync(Company Company);
    }
}
