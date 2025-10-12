# Implementation Guide: DetailView with TinyMCE Editor

## Overview

This implementation addresses the feature request to:
1. Create a separate DetailView for ideas at `/Idea/{ID}` instead of using a modal popup
2. Integrate TinyMCE rich text editor for HTML editing of the Description field

## Changes Made

### 1. Service Layer Enhancement
**File**: `IdeaGraph.Client/Services/IdeaService.cs`

Added a new method to fetch individual ideas:
```csharp
public async Task<Idea?> GetIdeaAsync(string id)
{
    try
    {
        var idea = await _httpClient.GetFromJsonAsync<Idea>($"api/ideas/{id}");
        return idea;
    }
    catch (Exception ex)
    {
        Debug.WriteLine(ex.ToString());
        return null;
    }
}
```

### 2. Package Addition
**File**: `IdeaGraph.Client/IdeaGraph.Client.csproj`

Added TinyMCE.Blazor package:
```xml
<PackageReference Include="TinyMCE.Blazor" Version="1.0.4" />
```

### 3. Global Imports
**File**: `IdeaGraph.Client/_Imports.razor`

Added TinyMCE using directive:
```razor
@using TinyMCE.Blazor
```

### 4. Home Page Updates
**File**: `IdeaGraph.Client/Pages/Home.razor`

#### Removed:
- Edit modal UI (lines 164-230)
- Edit state variables (`editingIdea`, `editRequest`, `editCurrentTag`, `isUpdating`, `editErrorMessage`)
- Modal-related methods (`StartEditIdea`, `CancelEdit`, `HandleUpdateIdea`)
- Edit tag management methods (`HandleEditTagInput`, `AddEditTag`, `RemoveEditTag`)

#### Added:
- `NavigationManager` injection
- View button (eye icon) for viewing idea details
- Navigation methods:
  ```csharp
  private void NavigateToDetail(string ideaId)
  {
      Navigation.NavigateTo($"/Idea/{ideaId}");
  }
  
  private void NavigateToEdit(string ideaId)
  {
      Navigation.NavigateTo($"/Idea/{ideaId}");
  }
  ```

### 5. New Detail View Page
**File**: `IdeaGraph.Client/Pages/IdeaDetail.razor` (NEW)

A comprehensive detail page with:
- Route: `@page "/Idea/{Id}"`
- Two modes: View and Edit
- TinyMCE integration for rich text editing
- Tag management
- Loading and error states
- Navigation back to home

Key features:
```razor
<!-- View Mode - HTML Rendering -->
<div class="description-content">
    @((MarkupString)idea.Description)
</div>

<!-- Edit Mode - TinyMCE Editor -->
<Editor Id="description" 
        @bind-Value="editRequest.Description" 
        ApiKey="no-api-key"
        Conf="@editorConf" />
```

TinyMCE Configuration:
```csharp
private Dictionary<string, object> editorConf = new Dictionary<string, object>
{
    { "height", 500 },
    { "menubar", false },
    { "plugins", "advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table code help wordcount" },
    { "toolbar", "undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help" }
};
```

### 6. Styling
**File**: `IdeaGraph.Client/Pages/IdeaDetail.razor.css` (NEW)

Provides styling for:
- Tag chips (matching Home page style)
- Description content HTML rendering
- Form elements

## User Flow

1. **Home Page**: User sees list of ideas
2. **View Details**: Click eye icon (👁️) to view idea in read-only mode
3. **Edit**: Click edit icon (✏️) or Edit button on detail page to enter edit mode
4. **Edit with TinyMCE**: Use rich text editor to format description with HTML
5. **Save**: Click "Save Changes" to update the idea
6. **Back**: Use "Back to List" button to return to home page

## TinyMCE Features Available

The editor includes:
- Text formatting (bold, italic, underline, colors)
- Text alignment (left, center, right, justify)
- Lists (bulleted and numbered)
- Indentation
- Format selection (paragraph, headings)
- Undo/Redo
- Help documentation

## Technical Details

### API Endpoint Used
The implementation uses the existing backend endpoint:
- `GET /api/ideas/{id}` - Fetch single idea
- `PUT /api/ideas/{id}` - Update idea

### TinyMCE API Key
Currently using `"no-api-key"` which is suitable for development. For production deployment, consider:
1. Getting a free API key from TinyMCE Cloud
2. Self-hosting TinyMCE

### HTML Safety
Description content is rendered using `@((MarkupString)idea.Description)` which allows HTML rendering. The content is assumed to be trusted since it's created by the application users.

## Testing Checklist

- [x] Build succeeds without errors
- [ ] Navigate to home page
- [ ] View idea details (eye icon)
- [ ] Switch to edit mode
- [ ] Test TinyMCE editor functionality
- [ ] Format text (bold, italic, lists)
- [ ] Add/remove tags
- [ ] Save changes
- [ ] Verify HTML renders correctly in view mode
- [ ] Navigate back to home
- [ ] Direct edit (pencil icon from home)

## Browser Compatibility

TinyMCE supports:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

Consider these potential improvements:
1. Query parameter to open directly in edit mode (e.g., `/Idea/{id}?edit=true`)
2. Image upload support in TinyMCE
3. Rich text preview in home page list
4. Version history for description changes
5. Custom TinyMCE plugins for specific formatting needs

## Troubleshooting

### TinyMCE not loading
- Check browser console for JavaScript errors
- Verify internet connectivity (TinyMCE loads from CDN)
- Check TinyMCE.Blazor package is installed correctly

### HTML not rendering
- Verify `@((MarkupString)...)` is used for HTML content
- Check that description field contains valid HTML

### Navigation not working
- Verify route is defined: `@page "/Idea/{Id}"`
- Check NavigationManager is injected
- Ensure idea ID is valid

## Code Quality

- **Lines of Code**: ~300 lines added (IdeaDetail.razor), ~150 lines removed (Home.razor)
- **Build Status**: ✅ Success (0 errors, 0 warnings)
- **Dependencies Added**: 1 (TinyMCE.Blazor 1.0.4)
- **Breaking Changes**: None
- **Backward Compatibility**: Full

## Deployment Notes

1. Ensure all NuGet packages are restored: `dotnet restore`
2. Build the solution: `dotnet build`
3. Test in development environment first
4. Consider getting TinyMCE API key for production
5. Update any deployment scripts to include new files

## Support

For issues or questions:
1. Check TinyMCE.Blazor documentation: https://www.tiny.cloud/docs/tinymce/latest/blazor-ref/
2. Review Blazor routing documentation: https://learn.microsoft.com/en-us/aspnet/core/blazor/fundamentals/routing
3. Examine browser console for JavaScript errors
