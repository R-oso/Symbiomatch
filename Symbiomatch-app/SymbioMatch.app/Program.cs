using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using SymbioMatch.app.Mapper;
using SymbioMatch.app.services.Queries.Handlers.Product;
using SymbioMatch.app.services.Queries.Handlers.UserProfile;
using SymbioMatch.app.services.Services;
using SymbioMatch.domain.Entities;
using SymbioMatch.domain.Repositories;
using SymbioMatch.infrastructure.Database;
using SymbioMatch.infrastructure.Queries;
using SymbioMatch.infrastructure.Queries.Products;
using SymbioMatch.infrastructure.Queries.Profile;
using SymbioMatch.infrastructure.Repositories;

var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<CompanyService>();
builder.Services.AddScoped<ProductService>();

// Repositories
builder.Services.AddScoped<ICompanyRepository, CompanyRepository>();
builder.Services.AddScoped<IProductRepository, ProductRepository>();

// Query Handlers
// Register the query handler
builder.Services.AddScoped<IGetProductByIdQueryHandler, GetProductByIdQueryHandler>();
builder.Services.AddScoped<IGetAllProductsQueryHandler, GetAllProductsQueryHandler>();
builder.Services.AddScoped<IGetAllProductsByCompanyQueryHandler, GetAllProductsByCompanyQueryHandler>();

builder.Services.AddScoped<IGetUserProfileQueryHandler, GetUserProfileQueryHandler>();

// Database context
builder.Services.AddDbContext<SymbioDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("MariaConnectionString"),
        new MySqlServerVersion(new Version(10, 6)) //
    ));



// Configure Identity
builder.Services.AddIdentity<ApplicationUser, IdentityRole>()
    .AddEntityFrameworkStores<SymbioDbContext>()
    .AddDefaultTokenProviders();

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddAutoMapper(typeof(AuthMappingProfile));


var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
