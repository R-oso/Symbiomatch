namespace SymbioMatch.app.services.DTOs.Auth
{
    public class RegisterDto
    {
        public string Firstname { get; set; }
        public string Lastname { get; set; }
        public string Email { get; set; }
        public string Phonenumber { get; set; }
        public string Password { get; set; }
        public Guid CompanyId { get; set; }
        public CompanyDto? NewCompany { get; set; }
    }
}
