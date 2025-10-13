window.cytoscapeInterop = {
    cyInstance: null,
    
    initializeCytoscape: function(containerId, elements) {
        try {
            // Register cose-bilkent layout if available
            if (typeof cytoscape !== 'undefined' && typeof cytoscapeCoseBilkent !== 'undefined') {
                cytoscape.use(cytoscapeCoseBilkent);
            }

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
                            'background-color': 'data(color)',
                            'label': 'data(label)',
                            'text-valign': 'top',
                            'text-halign': 'center',
                            'text-margin-y': -10,
                            'color': '#333',
                            'font-size': '10px',
                            'font-weight': 'normal',
                            'width': '40px',
                            'height': '40px'
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
                    name: 'cose-bilkent',
                    animate: false,
                    idealEdgeLength: 150,
                    nodeRepulsion: 4500,
                    edgeElasticity: 0.45,
                    nestingFactor: 0.1,
                    gravity: 0.25,
                    numIter: 2500,
                    tile: true,
                    tilingPaddingVertical: 10,
                    tilingPaddingHorizontal: 10,
                    gravityRangeCompound: 1.5,
                    gravityCompound: 1.0,
                    gravityRange: 3.8
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
