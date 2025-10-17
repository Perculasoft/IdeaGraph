using System.Diagnostics;
using System.Net.Http.Json;

namespace IdeaGraph.Client.Services
{
    /// <summary>
    /// Service for interacting with KiGate API via the proxy
    /// </summary>
    public class KiGateService
    {
        private readonly HttpClient _httpClient;

        public KiGateService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        /// <summary>
        /// Check health of KiGate API
        /// </summary>
        public async Task<KiGateHealthResponse?> GetHealthAsync()
        {
            try
            {
                var response = await _httpClient.GetFromJsonAsync<KiGateHealthResponse>("api/kigate/health");
                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        /// <summary>
        /// Get all available agents
        /// </summary>
        public async Task<List<AgentInfo>> GetAgentsAsync()
        {
            try
            {
                var agents = await _httpClient.GetFromJsonAsync<List<AgentInfo>>("api/kigate/agents");
                return agents ?? new List<AgentInfo>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<AgentInfo>();
            }
        }

        /// <summary>
        /// Execute an agent with a message
        /// </summary>
        public async Task<AgentExecutionResponse?> ExecuteAgentAsync(AgentExecutionRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/kigate/agent/execute", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<AgentExecutionResponse>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        /// <summary>
        /// Call OpenAI via KiGate
        /// </summary>
        public async Task<AiApiResult?> CallOpenAIAsync(AiApiRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/kigate/openai", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<AiApiResult>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        /// <summary>
        /// Call Gemini via KiGate
        /// </summary>
        public async Task<AiApiResult?> CallGeminiAsync(AiApiRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/kigate/gemini", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<AiApiResult>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        /// <summary>
        /// Call Claude via KiGate
        /// </summary>
        public async Task<AiApiResult?> CallClaudeAsync(AiApiRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/kigate/claude", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<AiApiResult>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        /// <summary>
        /// Create a GitHub issue via KiGate
        /// </summary>
        public async Task<GitHubIssueResponse?> CreateGitHubIssueAsync(GitHubIssueRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/kigate/github/create-issue", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<GitHubIssueResponse>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }
    }
}
