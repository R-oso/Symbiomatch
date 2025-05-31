using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using SymbioMatch.app.Models;
using SymbioMatch.app.services.Queries.Handlers.Product;
using SymbioMatch.app.services.Services;

namespace SymbioMatch.app.Controllers
{
    public class ProductController(IGetProductByIdQueryHandler productByIdQueryHandler,
                             IGetAllProductsQueryHandler getAllProductsQueryHandler,
                             IGetAllProductsByCompanyQueryHandler getAllProductsByCompanyQueryHandler,
                             ProductService productService,
                             IMapper mapper) : Controller
    {
        private readonly IGetProductByIdQueryHandler _productByIdQueryHandler = productByIdQueryHandler;
        private readonly IGetAllProductsQueryHandler _getAllProductsQueryHandler = getAllProductsQueryHandler;
        private readonly IGetAllProductsByCompanyQueryHandler _getAllProductsByCompanyQueryHandler = getAllProductsByCompanyQueryHandler;
        private readonly ProductService _productService = productService;
        private readonly IMapper _mapper = mapper;

        // Get product by ID
        [HttpGet("product/{id}")]
        public async Task<IActionResult> Details(Guid id)
        {
            var productResponse = await _productByIdQueryHandler.HandleAsync(id);
            if (productResponse == null)
            {
                return NotFound();
            }

            var viewModel = _mapper.Map<ProductViewModel>(productResponse);
            return View(viewModel);
        }

        // Get all products
        [HttpGet("products")]
        public async Task<IActionResult> AllProducts()
        {
            var products = await _getAllProductsQueryHandler.HandleAsync();
            var viewModels = _mapper.Map<List<ProductViewModel>>(products);
            return View(viewModels);
        }

        // Get all products by Company
        [HttpGet("products/company/{companyId}")]
        public async Task<IActionResult> ProductsByCompany(Guid companyId)
        {
            var products = await _getAllProductsByCompanyQueryHandler.HandleAsync(companyId);
            var viewModels = _mapper.Map<List<ProductViewModel>>(products);
            return View(viewModels);
        }
    }
}
