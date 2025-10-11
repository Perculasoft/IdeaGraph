using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using IdeaGraph.Client.Services;

namespace IdeaGraph.Client
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            var builder = WebAssemblyHostBuilder.CreateDefault(args);

            // Configure HttpClient for IdeaService
            builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
            builder.Services.AddScoped<IdeaService>(sp =>
            {
                var httpClient = sp.GetRequiredService<HttpClient>();
                // Use server base address for API calls
                httpClient.BaseAddress = new Uri(builder.Configuration["IdeaGraphApi:BaseUrl"] ?? builder.HostEnvironment.BaseAddress);
                return new IdeaService(httpClient);
            });

            await builder.Build().RunAsync();
        }
    }
}
