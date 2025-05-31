using System.ComponentModel.DataAnnotations;

namespace SymbioMatch.app.Models
{
    public class CompanyViewModel
    {
        public Guid Id { get; set; }
        public string? Name { get; set; } = string.Empty;
        [EmailAddress(ErrorMessage = "Invalid email address.")]
        public string Email { get; set; }

        [Phone(ErrorMessage = "Invalid phone number.")]
        public string Phonenumber { get; set; }
        public LocationViewModel Location { get; set; }
    }
}
