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
- Color-coded edges based on relationship types:
  - **Red**: depends_on
  - **Green**: extends
  - **Orange**: contradicts
  - **Purple**: synergizes_with
- Control buttons for "Fit to View" and "Reset Zoom"
- Loading states and error handling
- Responsive layout using force-directed (CoSE) algorithm

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

The graph uses the CoSE (Compound Spring Embedder) layout algorithm with the following key parameters:
- `idealEdgeLength`: 150px
- `nodeRepulsion`: 400000
- `gravity`: 80
- Auto-fitting to container on initialization

## Usage

Navigate to `/graph` in the application to view the graph visualization. Click on any node to navigate to that idea's detail page.
