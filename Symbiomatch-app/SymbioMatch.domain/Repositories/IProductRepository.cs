using SymbioMatch.domain.Entities;

namespace SymbioMatch.domain.Repositories
{
    public interface IProductRepository
    {
        Task<List<Product>> GetAllAsync();
        Task<Guid> InsertAsync(Product product);
        Task UpdateAsync(Product product);
    }
}
