namespace SymbioMatch.domain.Entities;

public class Location
{
    public Guid Id { get; set; }
    public string Country { get; set; }
    public string City { get; set; }
    public string Address { get; set; }
    public string PostalCode { get; set; }
    public string Latitude { get; set; }
    public string Longitude { get; set; }
}
