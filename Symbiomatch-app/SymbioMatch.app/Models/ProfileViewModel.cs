namespace SymbioMatch.app.Models
{
    public class ProfileViewModel
    {
        public string Firstname { get; set; }
        public string Lastname { get; set; }
        public string Email { get; set; }
        public string PhoneNumber { get; set; }
        public string CompanyName { get; set; }
        public List<MatchViewModel> MatchHistory { get; set; }
    }
}
