namespace SymbioMatch.app.Models
{
    public class MaterialViewModel
    {
        //public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public int Quantity { get; set; } = 0;
        public string Unit { get; set; } = string.Empty;
        public DateTime ExpiresAt { get; set; }
    }
}
