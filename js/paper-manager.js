class PaperManager {
    constructor() {
        this.papers = [];
        this.featured = [];
        this.monthlySnapshots = {};
        this.currentSlideIndex = 0;
        this.slideInterval = null;
    }

    async initialize() {
        await this.loadPapers();
        this.initializeFeaturedSlider();
        this.initializeMonthlySnapshot();
        this.initializeSearchableIndex();
    }

    async loadPapers() {
        try {
            const response = await fetch('paper_index.json');
            const data = await response.json();
            this.papers = data.papers;
            this.featured = data.featured;
            this.monthlySnapshots = data.monthly_snapshots;
        } catch (error) {
            console.error('Failed to load papers:', error);
        }
    }

    initializeFeaturedSlider() {
        const container = document.getElementById('featured-papers');
        if (!container) return;

        // Create slides for featured papers
        this.featured.forEach((paperId, index) => {
            const paper = this.papers.find(p => p.id === paperId);
            if (paper) {
                const slide = this.createFeaturedSlide(paper);
                slide.style.display = index === 0 ? 'block' : 'none';
                container.appendChild(slide);
            }
        });

        // Start auto-scroll
        this.slideInterval = setInterval(() => this.nextSlide(), 5000);

        // Add navigation controls
        container.addEventListener('mouseover', () => clearInterval(this.slideInterval));
        container.addEventListener('mouseout', () => {
            this.slideInterval = setInterval(() => this.nextSlide(), 5000);
        });
    }

    createFeaturedSlide(paper) {
        const slide = document.createElement('div');
        slide.className = 'featured-slide';
        slide.innerHTML = `
            <h3>${paper.title}</h3>
            <p class="author">${paper.author}</p>
            <p class="abstract">${paper.abstract.substring(0, 200)}...</p>
            <div class="keywords">
                ${paper.keywords.map(kw => `<span class="keyword">${kw}</span>`).join('')}
            </div>
            <a href="${paper.url}" class="btn primary">Read Paper</a>
        `;
        return slide;
    }

    nextSlide() {
        const slides = document.querySelectorAll('.featured-slide');
        slides[this.currentSlideIndex].style.display = 'none';
        this.currentSlideIndex = (this.currentSlideIndex + 1) % slides.length;
        slides[this.currentSlideIndex].style.display = 'block';
    }

    initializeMonthlySnapshot() {
        const container = document.getElementById('monthly-papers');
        if (!container) return;

        const currentMonth = new Date().toISOString().slice(0, 7);
        const monthlyPapers = this.monthlySnapshots[currentMonth] || [];

        container.innerHTML = monthlyPapers
            .map(paperId => this.papers.find(p => p.id === paperId))
            .filter(paper => paper)
            .map(paper => `
                <div class="paper-card">
                    <h3>${paper.title}</h3>
                    <p class="author">${paper.author}</p>
                    <div class="votes">
                        <button onclick="paperManager.vote('${paper.id}', 1)" class="vote-btn">👍</button>
                        <span id="votes-${paper.id}">${paper.votes || 0}</span>
                        <button onclick="paperManager.vote('${paper.id}', -1)" class="vote-btn">👎</button>
                    </div>
                    <a href="${paper.url}" class="btn secondary">Read More</a>
                </div>
            `).join('');
    }

    async vote(paperId, value) {
        // In a real implementation, this would call an API
        const voteSpan = document.getElementById(`votes-${paperId}`);
        const currentVotes = parseInt(voteSpan.textContent);
        voteSpan.textContent = currentVotes + value;
    }

    initializeSearchableIndex() {
        const container = document.getElementById('all-papers-list');
        const searchInput = document.getElementById('search-papers');
        const sortSelect = document.getElementById('sort-papers');
        
        if (!container || !searchInput || !sortSelect) return;

        const updatePapersList = () => {
            const query = searchInput.value.toLowerCase();
            const sortBy = sortSelect.value;

            let filteredPapers = this.papers.filter(paper =>
                paper.title.toLowerCase().includes(query) ||
                paper.author.toLowerCase().includes(query) ||
                paper.keywords.some(kw => kw.toLowerCase().includes(query)) ||
                paper.abstract.toLowerCase().includes(query)
            );

            // Sort papers
            filteredPapers.sort((a, b) => {
                switch (sortBy) {
                    case 'date-desc':
                        return new Date(b.date) - new Date(a.date);
                    case 'date-asc':
                        return new Date(a.date) - new Date(b.date);
                    case 'title':
                        return a.title.localeCompare(b.title);
                    default:
                        return 0;
                }
            });

            container.innerHTML = filteredPapers.map(paper => `
                <div class="paper-item">
                    <h3>${paper.title}</h3>
                    <p class="author">${paper.author}</p>
                    <p class="abstract">${paper.abstract.substring(0, 150)}...</p>
                    <div class="keywords">
                        ${paper.keywords.map(kw => `<span class="keyword">${kw}</span>`).join('')}
                    </div>
                    <a href="${paper.url}" class="btn secondary">View Paper</a>
                </div>
            `).join('');
        };

        searchInput.addEventListener('input', updatePapersList);
        sortSelect.addEventListener('change', updatePapersList);
        updatePapersList();
    }
}

// Initialize paper manager
const paperManager = new PaperManager();
document.addEventListener('DOMContentLoaded', () => {
    paperManager.initialize();
});
