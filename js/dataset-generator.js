class DatasetGenerator {
    constructor() {
        this.papers = [];
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;

        try {
            const response = await fetch('paper_index.json');
            const data = await response.json();
            this.papers = data.papers;
            this.setupEventListeners();
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize dataset generator:', error);
        }
    }

    setupEventListeners() {
        const generateBtn = document.getElementById('generate-btn');
        const downloadBtn = document.getElementById('download-btn');
        const formatSelect = document.getElementById('format-select');

        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                const format = formatSelect.value;
                const preview = this.generateDataset(format);
                document.getElementById('dataset-preview').textContent = preview;
            });
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                const format = formatSelect.value;
                const dataset = this.generateDataset(format);
                this.downloadDataset(dataset, format);
            });
        }
    }

    generateDataset(format) {
        const dataset = this.papers.map(paper => ({
            title: paper.title,
            abstract: paper.abstract,
            keywords: paper.keywords,
            metadata: {
                author: paper.author,
                date: paper.date,
                url: paper.url
            }
        }));

        // Split into train/val/test sets
        const shuffled = this.shuffle([...dataset]);
        const trainSize = Math.floor(shuffled.length * 0.7);
        const valSize = Math.floor(shuffled.length * 0.15);

        const splits = {
            train: shuffled.slice(0, trainSize),
            validation: shuffled.slice(trainSize, trainSize + valSize),
            test: shuffled.slice(trainSize + valSize)
        };

        switch (format) {
            case 'csv':
                return this.toCSV(splits);
            case 'jsonl':
                return this.toJSONL(splits);
            default:
                return JSON.stringify(splits, null, 2);
        }
    }

    shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    toCSV(splits) {
        const headers = ['split', 'title', 'abstract', 'keywords', 'author', 'date'];
        const rows = [headers.join(',')];

        Object.entries(splits).forEach(([split, data]) => {
            data.forEach(item => {
                rows.push([
                    split,
                    `"${item.title.replace(/"/g, '""')}"`,
                    `"${item.abstract.replace(/"/g, '""')}"`,
                    `"${item.keywords.join(';')}"`,
                    `"${item.metadata.author}"`,
                    item.metadata.date
                ].join(','));
            });
        });

        return rows.join('\n');
    }

    toJSONL(splits) {
        const lines = [];
        Object.entries(splits).forEach(([split, data]) => {
            data.forEach(item => {
                lines.push(JSON.stringify({
                    split,
                    ...item
                }));
            });
        });
        return lines.join('\n');
    }

    downloadDataset(content, format) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `csepp_dataset.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize dataset generator
const datasetGenerator = new DatasetGenerator();
document.addEventListener('DOMContentLoaded', () => {
    datasetGenerator.initialize();
});
