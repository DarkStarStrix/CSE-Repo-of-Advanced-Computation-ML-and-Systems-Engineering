class PaperGraph {
    constructor() {
        this.svg = null;
        this.simulation = null;
        this.data = null;
        this.nodes = [];
        this.links = [];
        this.width = window.innerWidth;
        this.height = window.innerHeight;
    }

    async initialize() {
        // Load paper data
        await this.loadData();
        this.setupGraph();
        this.setupControls();
    }

    async loadData() {
        try {
            const response = await fetch('paper_index.json');
            this.data = await response.json();
            this.processData();
        } catch (error) {
            console.error('Error loading paper data:', error);
        }
    }

    processData() {
        const papers = this.data.papers;
        const keywordMap = new Map();

        // Create nodes for papers
        this.nodes = papers.map(paper => ({
            id: paper.id,
            title: paper.title,
            author: paper.author,
            abstract: paper.abstract,
            keywords: paper.keywords,
            type: 'paper',
            url: paper.url
        }));

        // Create links based on shared keywords
        this.links = [];
        for (let i = 0; i < papers.length; i++) {
            for (let j = i + 1; j < papers.length; j++) {
                const sharedKeywords = papers[i].keywords.filter(
                    kw => papers[j].keywords.includes(kw)
                );
                if (sharedKeywords.length > 0) {
                    this.links.push({
                        source: papers[i].id,
                        target: papers[j].id,
                        value: sharedKeywords.length,
                        keywords: sharedKeywords
                    });
                }
            }
        }
    }

    setupGraph() {
        // Create SVG
        this.svg = d3.select('#graph')
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height);

        // Create force simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links)
                .id(d => d.id)
                .distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(30));

        // Create links
        const link = this.svg.append('g')
            .selectAll('line')
            .data(this.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.sqrt(d.value));

        // Create nodes
        const node = this.svg.append('g')
            .selectAll('.node')
            .data(this.nodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .call(this.drag(this.simulation));

        // Add circles to nodes
        node.append('circle')
            .attr('r', 8)
            .attr('fill', d => this.getColor(d));

        // Add labels to nodes
        node.append('text')
            .attr('dx', 12)
            .attr('dy', '.35em')
            .text(d => d.title.substring(0, 30));

        // Add title tooltips
        node.append('title')
            .text(d => d.title);

        // Update positions on tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Handle node click
        node.on('click', (event, d) => this.showInfo(d));
    }

    setupControls() {
        // Search functionality
        const searchBox = document.getElementById('search');
        searchBox.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            this.svg.selectAll('.node')
                .style('opacity', d => 
                    d.title.toLowerCase().includes(query) ||
                    d.keywords.some(k => k.toLowerCase().includes(query))
                        ? 1 : 0.1
                );
        });

        // Show/hide labels
        const labelToggle = document.getElementById('show-labels');
        labelToggle.addEventListener('change', (e) => {
            this.svg.selectAll('.node text')
                .style('display', e.target.checked ? 'block' : 'none');
        });

        // Link strength
        const strengthSlider = document.getElementById('link-strength');
        strengthSlider.addEventListener('input', (e) => {
            const strength = -e.target.value * 10;
            this.simulation.force('charge').strength(strength);
            this.simulation.alpha(1).restart();
        });
    }

    showInfo(paper) {
        const panel = document.getElementById('info-panel');
        document.getElementById('paper-title').textContent = paper.title;
        document.getElementById('paper-author').textContent = paper.author;
        document.getElementById('paper-abstract').textContent = paper.abstract;
        document.getElementById('paper-keywords').innerHTML = 
            paper.keywords.map(k => `<span class="keyword">${k}</span>`).join(' ');
        document.getElementById('paper-link').href = paper.url;
        panel.style.display = 'block';
    }

    getColor(node) {
        // Color nodes based on first keyword
        const colors = d3.schemeCategory10;
        const keyword = node.keywords[0] || '';
        const hash = keyword.split('').reduce((acc, char) => {
            return char.charCodeAt(0) + ((acc << 5) - acc);
        }, 0);
        return colors[Math.abs(hash) % colors.length];
    }

    drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
}

// Initialize graph when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const graph = new PaperGraph();
    graph.initialize();
});
