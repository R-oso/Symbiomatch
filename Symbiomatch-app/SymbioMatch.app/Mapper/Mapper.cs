using AutoMapper;
using SymbioMatch.app.Models;
using SymbioMatch.app.Models.Auth;
using SymbioMatch.app.services.DTOs;
using SymbioMatch.app.services.DTOs.Auth;
using SymbioMatch.app.services.Queries.Handlers.Matches;
using SymbioMatch.app.services.Queries.Handlers.Product;
using SymbioMatch.app.services.Queries.Handlers.UserProfile;
using SymbioMatch.domain.Entities;

namespace SymbioMatch.app.Mapper
{
    public class AuthMappingProfile : Profile
    {
        public AuthMappingProfile()
        {
            // Register
            CreateMap<RegisterViewModel, RegisterDto>()
                .ForMember(dest => dest.NewCompany, opt => opt.MapFrom(src => src.NewCompany));

            // Product
            CreateMap<ProductResponse, ProductViewModel>()
                .ForMember(dest => dest.Company, opt => opt.MapFrom(src => src.Company))
                .ForMember(dest => dest.Materials, opt => opt.MapFrom(src => src.Materials));
            CreateMap<ProductViewModel, ProductDto>();
            CreateMap<ProductDto, ProductViewModel>()
                .ForMember(dest => dest.Company, opt => opt.MapFrom(src => src.Company));

            // Material
            CreateMap<Material, MaterialViewModel>();

            // User Profile
            CreateMap<UserProfileResponse, ProfileViewModel>()
                .ForMember(dest => dest.MatchHistory, opt => opt.MapFrom(src => src.MatchHistory));

            // Match
            CreateMap<MatchResponse, MatchViewModel>()
                .ForMember(dest => dest.Product, opt => opt.MapFrom(src => src.Product))
                .ForMember(dest => dest.Company, opt => opt.MapFrom(src => src.Company));


            // Company
            CreateMap<CompanyDto, CompanyViewModel>();
            CreateMap<CompanyViewModel, CompanyDto>();
            CreateMap<Company, CompanyViewModel>();
        }
    }
}
