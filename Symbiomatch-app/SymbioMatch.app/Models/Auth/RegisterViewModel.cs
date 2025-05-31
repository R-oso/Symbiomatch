using System.ComponentModel.DataAnnotations;

namespace SymbioMatch.app.Models.Auth
{
    public class RegisterViewModel
    {
        [Required(ErrorMessage = "First name is required.")]
        [StringLength(50, ErrorMessage = "First name can't be longer than 100 characters.")]
        public string Firstname { get; set; }
        [Required(ErrorMessage = "Last name is required.")]
        [StringLength(50, ErrorMessage = "First name can't be longer than 100 characters.")]
        public string Lastname { get; set; }
        [Required(ErrorMessage = "Email is required.")]
        [EmailAddress(ErrorMessage = "Invalid email address.")]
        [StringLength(255, ErrorMessage = "Email can't be longer than 255 characters.")]
        public string Email { get; set; }

        [Phone(ErrorMessage = "Invalid phone number.")]
        [StringLength(15, ErrorMessage = "Phone number can't be longer than 15 characters.")]
        public string Phonenumber { get; set; }

        [Required(ErrorMessage = "Password is required.")]
        [StringLength(100, MinimumLength = 6, ErrorMessage = "Password must be at least 6 characters long.")]
        public string Password { get; set; }
        public Guid? CompanyId { get; set; }
        [Required(ErrorMessage = "You have to be part of a company to register.")]
        public CompanyViewModel NewCompany { get; set; }
    }
}
