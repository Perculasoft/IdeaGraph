# Graph Visualization with Cytoscape.js

This document describes the implementation of the graph visualization feature using Cytoscape.js to display ideas and their relationships.

## Overview

The `/graph` route displays an interactive graph visualization of all ideas and their relationships using Cytoscape.js. The implementation includes:

- **Graph.razor**: The main page component that loads and displays the graph
- **RelationService.cs**: Service to fetch relationship data from the API
- **cytoscape-interop.js**: JavaScript interop layer for Cytoscape.js integration
- **Relation model**: Client-side model for relationship data

## Features

- Interactive graph with zoom and pan capabilities
- Node clicking to navigate to idea details
- **Status-based node coloring**: Each idea node is colored based on its status:
  - **Indigo**: New
  - **Purple**: Concept
  - **Blue**: Specification
  - **Green**: Ready
  - **Dark Green**: Implemented
  - **Gray**: Discarded
- **Labels displayed above nodes**: Node titles appear above the nodes in a small, readable font
- Color-coded edges based on relationship types:
  - **Red**: depends_on
  - **Green**: extends
  - **Orange**: contradicts
  - **Purple**: synergizes_with
- Control buttons for "Fit to View" and "Reset Zoom"
- Loading states and error handling
- Responsive layout using improved force-directed layout (CoSE-Bilkent algorithm)

## Technical Details

### Data Flow

1. On page load, `Graph.razor` fetches all ideas using `IdeaService`
2. For each idea, it fetches relations using `RelationService`
3. Relations are deduplicated by ID
4. Data is transformed into Cytoscape.js format (nodes and edges)
5. JavaScript interop initializes the Cytoscape instance

### API Endpoints Used

- `GET /api/ideas` - Fetch all ideas
- `GET /api/relations/{ideaId}` - Fetch relations for a specific idea

### Cytoscape.js Configuration

The graph uses the CoSE-Bilkent (Compound Spring Embedder - Bilkent University) layout algorithm, which provides better graph visualization compared to the standard CoSE layout. Key parameters:
- `idealEdgeLength`: 150px
- `nodeRepulsion`: 4500
- `gravity`: 0.25
- `numIter`: 2500 (number of iterations for better layout quality)
- `tile`: true (for better space utilization)
- Node size: 40x40px
- Labels positioned above nodes with 10px margin

The layout is specifically optimized for displaying ideas and their relationships with clear visual separation.

#### Library Loading

The Cytoscape.js library and the cose-bilkent extension are loaded via CDN in `App.razor`:
```html
<script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
```

When loaded via CDN script tags, the cose-bilkent extension automatically registers itself with Cytoscape. No manual registration is needed in the JavaScript code.

## Usage

Navigate to `/graph` in the application to view the graph visualization. Click on any node to navigate to that idea's detail page.
