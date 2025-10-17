using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using IdeaGraph.Client.Services;

namespace IdeaGraph.Client
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            var builder = WebAssemblyHostBuilder.CreateDefault(args);

            // Configure HttpClient for IdeaService to call the ASP.NET Core server API
            builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
            builder.Services.AddScoped<IdeaService>();
            builder.Services.AddScoped<RelationService>();
            builder.Services.AddScoped<SectionService>();

            await builder.Build().RunAsync();
        }
    }
}
