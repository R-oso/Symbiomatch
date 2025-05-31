namespace SymbioMatch.app.services.DTOs
{
    public class CompanyDto
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Contact { get; set; }
        public LocationDto Location { get; set; }
    }
}
