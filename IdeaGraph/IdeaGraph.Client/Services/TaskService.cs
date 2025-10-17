using System.Diagnostics;
using System.Net.Http.Json;
using IdeaGraph.Client.Models;

namespace IdeaGraph.Client.Services
{
    public class TaskService
    {
        private readonly HttpClient _httpClient;

        public TaskService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<IdeaTask>> GetTasksAsync()
        {
            try
            {
                var tasks = await _httpClient.GetFromJsonAsync<List<IdeaTask>>("api/tasks");
                return tasks ?? new List<IdeaTask>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<IdeaTask>();
            }
        }

        public async Task<List<IdeaTask>> GetTasksByIdeaAsync(string ideaId)
        {
            try
            {
                var response = await _httpClient.GetAsync($"api/tasks/idea/{ideaId}");

                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return new List<IdeaTask>();
                }

                response.EnsureSuccessStatusCode();

                var tasks = await response.Content.ReadFromJsonAsync<List<IdeaTask>>();
                return tasks ?? new List<IdeaTask>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return new List<IdeaTask>();
            }
        }

        public async Task<IdeaTask?> GetTaskAsync(string id)
        {
            try
            {
                var task = await _httpClient.GetFromJsonAsync<IdeaTask>($"api/tasks/{id}");
                return task;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<IdeaTask?> CreateTaskAsync(TaskCreateRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("api/tasks", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<IdeaTask>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<IdeaTask?> UpdateTaskAsync(string id, TaskUpdateRequest request)
        {
            try
            {
                var response = await _httpClient.PutAsJsonAsync($"api/tasks/{id}", request);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<IdeaTask>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<bool> DeleteTaskAsync(string id)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"api/tasks/{id}");
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return false;
            }
        }

        public async Task<IdeaTask?> ImproveTaskAsync(string id)
        {
            try
            {
                var response = await _httpClient.PostAsync($"api/tasks/{id}/improve", null);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<IdeaTask>();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                Debug.WriteLine(ex.ToString());
                return null;
            }
        }

        public async Task<GitHubIssueResponse?> CreateGitHubIssueAsync(string id)
        {
            try
            {
                var response = await _httpClient.PostAsync($"api/tasks/{id}/github-issue", null);
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
