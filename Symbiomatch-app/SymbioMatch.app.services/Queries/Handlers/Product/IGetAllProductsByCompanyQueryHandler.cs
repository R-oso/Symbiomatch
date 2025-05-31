namespace SymbioMatch.app.services.Queries.Handlers.Product
{
    public interface IGetAllProductsByCompanyQueryHandler
    {
        Task<List<ProductResponse>> HandleAsync(Guid companyId);
    }
}
