namespace SymbioMatch.domain.Entities
{
    public class Material
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Category { get; set; }
        public int AvailableQuantity { get; set; }
        public string UnitOfMeasure { get; set; }
        public DateTime ExpiresAt { get; set; }
        public Guid ProductId { get; set; }
        public Product Product { get; set; }
    }
}
