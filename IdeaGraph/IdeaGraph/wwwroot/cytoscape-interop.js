window.cytoscapeInterop = {
    cyInstance: null,
    
    initializeCytoscape: function(containerId, elements) {
        try {
            // Destroy existing instance if any
            if (this.cyInstance) {
                this.cyInstance.destroy();
                this.cyInstance = null;
            }

            // Check if container exists
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('Container element not found:', containerId);
                return false;
            }

            // Initialize Cytoscape
            this.cyInstance = cytoscape({
                container: container,
                elements: elements,
                style: [
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#3b82f6',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': '#fff',
                            'text-outline-color': '#3b82f6',
                            'text-outline-width': 2,
                            'font-size': '12px',
                            'width': '50px',
                            'height': '50px'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 2,
                            'line-color': '#94a3b8',
                            'target-arrow-color': '#94a3b8',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'label': 'data(label)',
                            'font-size': '10px',
                            'text-rotation': 'autorotate',
                            'text-margin-y': -10
                        }
                    },
                    {
                        selector: 'edge[relationType="depends_on"]',
                        style: {
                            'line-color': '#ef4444',
                            'target-arrow-color': '#ef4444'
                        }
                    },
                    {
                        selector: 'edge[relationType="extends"]',
                        style: {
                            'line-color': '#10b981',
                            'target-arrow-color': '#10b981'
                        }
                    },
                    {
                        selector: 'edge[relationType="contradicts"]',
                        style: {
                            'line-color': '#f59e0b',
                            'target-arrow-color': '#f59e0b'
                        }
                    },
                    {
                        selector: 'edge[relationType="synergizes_with"]',
                        style: {
                            'line-color': '#8b5cf6',
                            'target-arrow-color': '#8b5cf6'
                        }
                    },
                    {
                        selector: ':selected',
                        style: {
                            'background-color': '#f59e0b',
                            'line-color': '#f59e0b',
                            'target-arrow-color': '#f59e0b',
                            'source-arrow-color': '#f59e0b'
                        }
                    }
                ],
                layout: {
                    name: 'cose',
                    idealEdgeLength: 150,
                    nodeOverlap: 20,
                    refresh: 20,
                    fit: true,
                    padding: 30,
                    randomize: false,
                    componentSpacing: 100,
                    nodeRepulsion: 400000,
                    edgeElasticity: 100,
                    nestingFactor: 5,
                    gravity: 80,
                    numIter: 1000,
                    initialTemp: 200,
                    coolingFactor: 0.95,
                    minTemp: 1.0
                }
            });

            // Add click event to nodes
            this.cyInstance.on('tap', 'node', function(evt) {
                const node = evt.target;
                const ideaId = node.data('id');
                console.log('Node clicked:', ideaId);
                // Navigate to idea detail page
                window.location.href = `/ideas/${ideaId}`;
            });

            return true;
        } catch (error) {
            console.error('Error initializing Cytoscape:', error);
            return false;
        }
    },

    destroy: function() {
        if (this.cyInstance) {
            this.cyInstance.destroy();
            this.cyInstance = null;
        }
    },

    fitToView: function() {
        if (this.cyInstance) {
            this.cyInstance.fit();
        }
    },

    resetZoom: function() {
        if (this.cyInstance) {
            this.cyInstance.reset();
        }
    }
};
