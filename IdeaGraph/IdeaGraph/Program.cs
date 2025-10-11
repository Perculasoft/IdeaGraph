using IdeaGraph.Components;
using IdeaGraph.Services;
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

            // Add API controller support
            builder.Services.AddControllers();

            // Configure HttpClient for server's IdeaService to call FastAPI
            var ideaGraphApiUrl = builder.Configuration["IdeaGraphApi:BaseUrl"] ?? "http://localhost:8000/";
            builder.Services.AddHttpClient<IdeaGraph.Services.IdeaService>(client =>
            {
                client.BaseAddress = new Uri(ideaGraphApiUrl);
            });

            // Configure HttpClient for client's IdeaService to call server API
            builder.Services.AddScoped<IdeaGraph.Client.Services.IdeaService>(sp =>
            {
                var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
                var httpClient = httpClientFactory.CreateClient();
                httpClient.BaseAddress = new Uri(builder.Configuration["BaseAddress"] ?? "http://localhost:5000/");
                return new IdeaGraph.Client.Services.IdeaService(httpClient);
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
