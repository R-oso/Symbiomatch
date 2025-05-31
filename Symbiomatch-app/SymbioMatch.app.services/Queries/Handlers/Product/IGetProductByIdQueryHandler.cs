namespace SymbioMatch.app.services.Queries.Handlers.Product
{
    public interface IGetProductByIdQueryHandler
    {
        Task<ProductResponse?> HandleAsync(Guid id);
    }
}
