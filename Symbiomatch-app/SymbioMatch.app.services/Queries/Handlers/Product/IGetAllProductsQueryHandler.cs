namespace SymbioMatch.app.services.Queries.Handlers.Product
{
    public interface IGetAllProductsQueryHandler
    {
        Task<List<ProductResponse>> HandleAsync();
    }
}
