namespace SymbioMatch.app.Models
{
    public class ProductViewModel
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime CreatedOn { get; set; } = DateTime.Now;
        public List<MaterialViewModel> Materials { get; set; } = [];
        public CompanyViewModel? Company { get; set; }
    }
}
