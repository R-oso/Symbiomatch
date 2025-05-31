using Microsoft.EntityFrameworkCore;
using SymbioMatch.domain.Entities;
using SymbioMatch.domain.Repositories;
using SymbioMatch.infrastructure.Database;

namespace SymbioMatch.infrastructure.Repositories
{
    public sealed class ProductRepository(SymbioDbContext dbContext) : IProductRepository
    {
        private readonly SymbioDbContext _dbContext = dbContext;

        public async Task<List<Product>> GetAllAsync()
        {
            return await _dbContext.Products.ToListAsync();
        }

        public async Task<Guid> InsertAsync(Product product)
        {
            _dbContext.Products.Add(product);

            await _dbContext.SaveChangesAsync();

            return product.Id;
        }

        public async Task UpdateAsync(Product product)
        {
            _dbContext.Products.Update(product);

            await _dbContext.SaveChangesAsync();
        }
    }
}
