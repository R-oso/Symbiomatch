namespace SymbioMatch.domain.Entities;
public class Product
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public DateTime CreatedOn { get; set; }
    public DateTime ExpiresAt { get; set; }
    public List<Material> Materials { get; set; } = [];
    public Guid CompanyId { get; set; }
    public Company Company { get; set; }
}
