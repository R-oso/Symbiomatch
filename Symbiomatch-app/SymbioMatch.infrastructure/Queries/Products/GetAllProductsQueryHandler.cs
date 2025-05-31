using Microsoft.EntityFrameworkCore;
using SymbioMatch.app.services.Queries.Handlers.Product;
using SymbioMatch.infrastructure.Database;

namespace SymbioMatch.infrastructure.Queries.Products;

public class GetAllProductsQueryHandler(SymbioDbContext context) : IGetAllProductsQueryHandler
{
    private readonly SymbioDbContext _context = context;

    public async Task<List<ProductResponse>> HandleAsync()
    {
        var products = await _context.Products
                        .Include(p => p.Materials)
                        .Include(p => p.Company)
                        .ToListAsync();

        // Mapping the products to ProductResponse DTOs
        var productResponses = products.Select(product => new ProductResponse
        {
            Id = product.Id,
            Name = product.Name,
            CreatedOn = product.CreatedOn,
            Materials = product.Materials,
            Company = product.Company
        }).ToList();

        return productResponses;
    }
}
