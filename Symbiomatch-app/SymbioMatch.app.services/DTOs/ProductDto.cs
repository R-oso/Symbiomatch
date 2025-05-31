namespace SymbioMatch.app.services.DTOs
{
    public class ProductDto
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime CreatedOn { get; set; }
        // public List<MaterialDto> Materials { get; set; } = [];
        public CompanyDto? Company { get; set; }
    }
}

