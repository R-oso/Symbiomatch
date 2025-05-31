using SymbioMatch.domain.Repositories;

namespace SymbioMatch.app.services.Services
{
    public sealed class ProductService(IProductRepository productRepository)
    {
        private readonly IProductRepository _productRepository = productRepository;

        // Methods (Create, Update, Delete)
    }
}
