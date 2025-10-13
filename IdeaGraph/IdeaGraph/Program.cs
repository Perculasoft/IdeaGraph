using IdeaGraph.Components;
using IdeaGraph.Client.Services;

namespace IdeaGraph
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.
            builder.Services.AddRazorComponents()
                .AddInteractiveServerComponents()
                .AddInteractiveWebAssemblyComponents();

            // Add CORS policy for Blazor WebAssembly
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowAll", policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });

            // Add API controller support
            builder.Services.AddControllers();
                     
            // Add API Controllers
            builder.Services.AddControllers();

            // Configure HttpClient for FastAPI (used by controllers)
            var fastApiUrl = builder.Configuration["FastAPI:BaseUrl"] ?? "https://api.angermeier.net";
            var xApiKey = builder.Configuration["FastAPI:X-Api-Key"] ?? "";
            builder.Services.AddHttpClient("FastAPI", client =>
            {
                client.BaseAddress = new Uri(fastApiUrl);
                client.Timeout = TimeSpan.FromSeconds(30);
                // Add X-Api-Key header if configured
                if (!string.IsNullOrEmpty(xApiKey))
                {
                    client.DefaultRequestHeaders.Add("X-Api-Key", xApiKey);
                }
            });

            // Configure HttpClient for IdeaService (now points to local API)
            var ideaGraphApiUrl = builder.Configuration["IdeaGraphApi:BaseUrl"] ?? "https://localhost:5001/api/";
            builder.Services.AddHttpClient<IdeaService>(client =>
            {
                client.BaseAddress = new Uri(ideaGraphApiUrl);
            });

            // Configure HttpClient for client's IdeaService to call server API
            // For server-side Blazor, we need to call the API on the same server
            // Use NavigationManager at runtime to get the correct base URL
            builder.Services.AddScoped<IdeaGraph.Client.Services.IdeaService>(sp =>
            {
                var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
                var httpClient = httpClientFactory.CreateClient();
                var navManager = sp.GetRequiredService<Microsoft.AspNetCore.Components.NavigationManager>();
                httpClient.BaseAddress = new Uri(navManager.BaseUri);
                return new IdeaGraph.Client.Services.IdeaService(httpClient);
            });
            
            // Configure HttpClient for client's RelationService to call server API
            builder.Services.AddScoped<IdeaGraph.Client.Services.RelationService>(sp =>
            {
                var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
                var httpClient = httpClientFactory.CreateClient();
                var navManager = sp.GetRequiredService<Microsoft.AspNetCore.Components.NavigationManager>();
                httpClient.BaseAddress = new Uri(navManager.BaseUri);
                return new IdeaGraph.Client.Services.RelationService(httpClient);
            });
            
            builder.Services.AddHttpClient();

            var app = builder.Build();

            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.UseWebAssemblyDebugging();
            }
            else
            {
                app.UseExceptionHandler("/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseHttpsRedirection();

            // Enable CORS
            app.UseCors("AllowAll");

            app.UseAntiforgery();

            app.MapStaticAssets();
            app.MapControllers();
            
            app.MapRazorComponents<App>()
                .AddInteractiveServerRenderMode()
                .AddInteractiveWebAssemblyRenderMode()
                .AddAdditionalAssemblies(typeof(Client._Imports).Assembly);

            app.Run();
        }
    }
}
