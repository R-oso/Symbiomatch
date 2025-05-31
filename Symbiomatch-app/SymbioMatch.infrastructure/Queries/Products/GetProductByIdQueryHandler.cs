using Microsoft.EntityFrameworkCore;
using SymbioMatch.app.services.Queries.Handlers.Product;
using SymbioMatch.infrastructure.Database;

namespace SymbioMatch.infrastructure.Queries.Products
{
    public class GetProductByIdQueryHandler(SymbioDbContext context) : IGetProductByIdQueryHandler
    {
        private readonly SymbioDbContext _context = context;

        public async Task<ProductResponse?> HandleAsync(Guid id)
        {
            var product = await _context.Products
                            .Include(p => p.Materials)
                            .Include(p => p.Company)
                            .FirstOrDefaultAsync(p => p.Id == id);

            return new ProductResponse
            {
                Id = product.Id,
                Name = product.Name,
                CreatedOn = product.CreatedOn,
                Materials = product.Materials,
                Company = product.Company
            };
        }
    }
}
