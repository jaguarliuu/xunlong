# Report Generation

XunLong excels at generating comprehensive, well-researched reports on any topic with minimal input.

## Overview

The Report Generation feature automatically:
- 🔍 Researches your topic across the web
- 📊 Structures findings logically
- ✍️ Writes professional content
- 📚 Cites all sources
- 📄 Exports to multiple formats

### What's New (2025)

Recent pipeline upgrades deliver higher quality output with lower latency:

- **Section-Level Agents** – every outline node spins up its own writer and reviewer, so chapters are drafted, evaluated, and enhanced in parallel.
- **Built-in Visualization Pass** – each section is analysed for tabular or chart-worthy data; when required the data-visualization agent emits HTML-ready tables or chart specs.
- **Time-Aware Research** – the deep-search layer now understands queries such as “daily report” or explicit dates, applies DuckDuckGo date filters, and prioritises chronologically relevant sources.
- **Clean HTML Rendering** – headings are de-duplicated, Markdown is normalised before rendering, and the academic template consumes pre-rendered section fragments to avoid formatting drift.

## Quick Start

```bash
python xunlong.py report "AI Industry Trends 2025"
```

That's it! XunLong handles the rest.

## Report Styles

XunLong supports three professional report styles:

### Business Style 💼

**Best for:** Market analysis, industry reports, business intelligence

**Characteristics:**
- Executive summary with key takeaways
- Data-driven insights
- Professional tone
- Charts and tables
- ROI and metrics focus

**Example:**
```bash
python xunlong.py report "Electric Vehicle Market Analysis" \
  --style business \
  --depth comprehensive
```

**Sample Output Structure:**
```
├── Executive Summary
├── Market Overview
│   ├── Market Size & Growth
│   └── Key Players
├── Trend Analysis
├── Competitive Landscape
├── Opportunities & Challenges
└── Recommendations
```

### Academic Style 🎓

**Best for:** Research summaries, literature reviews, academic papers

**Characteristics:**
- Abstract and introduction
- Rigorous citations
- Methodological approach
- Literature review sections
- Formal academic tone

**Example:**
```bash
python xunlong.py report "Machine Learning in Healthcare" \
  --style academic \
  --depth comprehensive
```

**Sample Output Structure:**
```
├── Abstract
├── Introduction
├── Literature Review
├── Methodology
├── Findings
├── Discussion
├── Conclusion
└── References
```

### Technical Style 🔧

**Best for:** Technology deep-dives, API documentation, technical specifications

**Characteristics:**
- Technical accuracy
- Code examples
- Architecture diagrams
- Implementation details
- Best practices

**Example:**
```bash
python xunlong.py report "GraphQL vs REST APIs" \
  --style technical \
  --depth comprehensive
```

**Sample Output Structure:**
```
├── Overview
├── Technical Architecture
├── Core Concepts
├── Implementation Guide
├── Code Examples
├── Performance Analysis
└── Best Practices
```

## Depth Levels

Control the level of detail with the `--depth` parameter:

| Depth | Time | Words | Best For |
|-------|------|-------|----------|
| **overview** | ~5 min | 1,500-2,000 | Quick summaries, initial research |
| **standard** | ~10 min | 3,000-4,000 | Most use cases, balanced detail |
| **comprehensive** | ~20 min | 6,000-8,000 | In-depth analysis, presentations |

**Examples:**

```bash
# Quick overview
python xunlong.py report "Quantum Computing" --depth overview

# Balanced report (default)
python xunlong.py report "Quantum Computing" --depth standard

# Deep dive
python xunlong.py report "Quantum Computing" --depth comprehensive
```

## Advanced Features

### Section-Oriented Pipeline

1. **Outline Planning** – the coordinator produces a structured outline (id, title, requirements, word budget).
2. **Parallel Section Agents** – each outline item is assigned to a dedicated writer that drafts content with awareness of neighbouring sections.
3. **Automatic Visualisation** – if a section contains structured data, a visualiser agent decides whether to embed tables or charts and generates ready-to-render HTML fragments.
4. **Quality Gate & Rewrite Loop** – evaluators score each section for coverage and coherence; low scoring sections are rewritten until they pass or reach the retry limit.
5. **HTML Assembly** – the final assembler streams the pre-rendered section HTML into the document template, ensuring headings, tables, and charts remain stable.

Because every stage runs asynchronously the full report finishes noticeably faster, especially for comprehensive or daily reports with strict timelines.

### Custom Sections

Specify exactly what sections you want:

```bash
python xunlong.py report "AI Ethics" \
  --sections "Introduction,Current Challenges,Case Studies,Future Outlook"
```

### Time-Bounded Research
The search layer now applies automatic date filters:

- Queries containing phrases like “daily report”, specific dates, or “today/yesterday” are scoped to the appropriate day or week automatically.
- DuckDuckGo searches include `df=` parameters so only fresh sources are retrieved.

You can still force a manual window when needed:

```bash
python xunlong.py report "COVID-19 Vaccines" \
  --time-range "last-6-months"
```

### Language Support

Generate reports in multiple languages:

```bash
python xunlong.py report "气候变化影响" --language zh-CN
python xunlong.py report "Climate Change Impact" --language en-US
```

### Source Filtering

Control what sources are used:

```bash
# Only academic sources
python xunlong.py report "Dark Matter" \
  --sources academic

# News sources only
python xunlong.py report "Tech Industry Layoffs" \
  --sources news

# All sources (default)
python xunlong.py report "AI Trends" \
  --sources all
```

## Output Formats

### Markdown (Default)

```bash
python xunlong.py report "Topic" --format md
```

**Features:**
- Clean, readable text
- Easy to edit
- Version control friendly
- Portable

### HTML

```bash
python xunlong.py report "Topic" --format html
```

**Features:**
- Academic-styled template with pre-rendered section HTML
- Stable table of contents and anchors
- Responsive design with inline tables/charts
- Print-ready output

### PDF

```bash
python xunlong.py report "Topic" --format pdf
```

**Features:**
- Professional layout
- Page numbers
- Headers/footers
- Ready to share

### DOCX

```bash
python xunlong.py report "Topic" --format docx
```

**Features:**
- Microsoft Word compatible
- Editable formatting
- Comments support
- Track changes ready

### Multiple Formats

```bash
python xunlong.py report "Topic" --format md,html,pdf,docx
```

All formats are generated simultaneously.

## Report Quality

### Citations

Every fact is cited with:
- Source URL
- Publication date
- Author (when available)
- Access date

**Example Citation:**
```markdown
According to recent research, AI adoption has increased by 67% [1].

## References
[1] Smith, J. (2025). "AI in Enterprise." TechReview.
    https://example.com/ai-enterprise
    Accessed: 2025-10-05
```

### Quality Metrics

XunLong tracks:
- **Citation Coverage**: % of claims cited (target: >80%)
- **Source Diversity**: Number of unique sources (target: >10)
- **Readability Score**: Flesch reading ease (target: 60-70)
- **Coherence Score**: Logical flow rating (target: >0.85)

View metrics:
```bash
python xunlong.py stats <project-id>
```

### Fact-Checking

Reports undergo automatic fact-checking:
- ✅ Date verification
- ✅ Statistical consistency
- ✅ Source credibility check
- ✅ Claim cross-referencing

## Example Workflow

### 1. Generate Initial Report

```bash
python xunlong.py report "Renewable Energy Trends 2025" \
  --style business \
  --depth standard \
  --format md,pdf
```

**Output:**
```
✅ Report generated successfully!

📊 Statistics:
   - Duration: 8m 34s
   - Words: 3,847
   - Citations: 23 sources
   - Quality Score: 0.89

📁 Files:
   - storage/20251005_143022_renewable_energy/reports/FINAL_REPORT.md
   - storage/20251005_143022_renewable_energy/exports/report.pdf

🔗 Project ID: 20251005_143022
```

### 2. Review Content

```bash
cat storage/20251005_143022_renewable_energy/reports/FINAL_REPORT.md
```

### 3. Request Modifications

```bash
python xunlong.py iterate 20251005_143022 \
  "Add a section on solar energy costs and expand the wind energy section"
```

### 4. Export Additional Formats

```bash
python xunlong.py export 20251005_143022 --format docx,html
```

## Best Practices

### 📝 Writing Effective Queries

**Good:**
- "AI ethics challenges in autonomous vehicles"
- "Impact of remote work on productivity 2025"
- "Comparison of Python vs JavaScript for web development"

**Less Effective:**
- "AI" (too broad)
- "stuff about work" (too vague)
- "tell me everything about programming" (unfocused)

### 🎯 Choosing the Right Style

| Your Goal | Recommended Style |
|-----------|------------------|
| Investor presentation | Business |
| Research paper | Academic |
| Internal tech doc | Technical |
| Blog post | Business (lighter tone) |
| White paper | Academic or Business |

### ⚡ Optimizing Generation Time

**Fast (~5 min):**
```bash
python xunlong.py report "Topic" \
  --depth overview \
  --model gpt-3.5-turbo
```

**Balanced (~10 min):**
```bash
python xunlong.py report "Topic" \
  --depth standard \
  --model gpt-4o-mini
```

**High Quality (~20 min):**
```bash
python xunlong.py report "Topic" \
  --depth comprehensive \
  --model gpt-4o
```

## Troubleshooting

### Issue: "No relevant sources found"

**Solutions:**
- Make your query more specific
- Check your internet connection
- Try different search terms
- Verify topic is searchable

### Issue: Report is too short

**Solutions:**
- Increase depth: `--depth comprehensive`
- Add more sections: `--sections "Section1,Section2,..."`
- Use slower, more powerful model: `--model gpt-4o`

### Issue: Citations missing

**Solutions:**
- Enable strict citations: `--strict-citations`
- Increase source count: `--min-sources 15`
- Check search results quality

### Issue: Generation failed mid-way

**Solutions:**
```bash
# Resume from checkpoint
python xunlong.py resume <project-id>

# Check error logs
cat storage/<project-id>/logs/generation.log
```

## API Reference

### Command Structure

```bash
python xunlong.py report <query> [options]
```

### Required Arguments

- `<query>`: Topic or research question

### Optional Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--style` | str | `business` | Report style (business/academic/technical) |
| `--depth` | str | `standard` | Detail level (overview/standard/comprehensive) |
| `--format` | str | `md` | Output formats (md,html,pdf,docx) |
| `--language` | str | `en-US` | Report language |
| `--sections` | str | Auto | Custom section list |
| `--time-range` | str | `all` | Research time window |
| `--sources` | str | `all` | Source type filter |
| `--model` | str | `gpt-4o-mini` | LLM model to use |
| `--min-sources` | int | `10` | Minimum sources required |
| `--strict-citations` | flag | `false` | Enforce citation on every claim |

## Examples

### Market Research Report

```bash
python xunlong.py report "Global Smartphone Market 2025" \
  --style business \
  --depth comprehensive \
  --sections "Market Size,Top Players,Trends,Forecast,Recommendations" \
  --format pdf,docx
```

### Academic Literature Review

```bash
python xunlong.py report "Deep Learning in Medical Imaging" \
  --style academic \
  --depth comprehensive \
  --sources academic \
  --strict-citations \
  --format md,pdf
```

### Technical Documentation

```bash
python xunlong.py report "Kubernetes Best Practices 2025" \
  --style technical \
  --depth standard \
  --format md,html
```

### Quick News Summary

```bash
python xunlong.py report "Latest AI Developments" \
  --depth overview \
  --time-range last-week \
  --sources news \
  --format md
```

## Next Steps

- Learn about [Fiction Writing](/guide/features/fiction)
- Explore [PPT Creation](/guide/features/ppt)
- Understand [Content Iteration](/guide/features/iteration)
- Check [Export Formats](/guide/features/export)
