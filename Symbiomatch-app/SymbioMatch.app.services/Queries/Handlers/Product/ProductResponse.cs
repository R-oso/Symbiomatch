using SymbioMatch.domain.Entities;

namespace SymbioMatch.app.services.Queries.Handlers.Product
{
    public class ProductResponse
    {
        public Guid Id { get; set; } = Guid.Empty;
        public string Name { get; set; } = string.Empty;
        public DateTime CreatedOn { get; set; }
        public List<Material> Materials { get; set; } = [];
        public Company Company { get; set; }
    }
}
