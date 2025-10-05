# CLI Reference

XunLong provides a comprehensive command-line interface for all content generation tasks.

## Installation

```bash
# Install XunLong
pip install -r requirements.txt

# Verify installation
python xunlong.py --version
```

## Global Options

```bash
python xunlong.py [COMMAND] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--help` | Show help message |

## Commands Overview

| Command | Purpose | Quick Example |
|---------|---------|---------------|
| [`report`](#report) | Generate research reports | `xunlong.py report "AI Trends"` |
| [`fiction`](#fiction) | Create fiction stories | `xunlong.py fiction "Mystery novel"` |
| [`ppt`](#ppt) | Generate presentations | `xunlong.py ppt "Product Launch"` |
| [`export`](#export) | Export to different formats | `xunlong.py export <id> --type pdf` |
| [`iterate`](#iterate) | Refine existing content | `xunlong.py iterate <id> "Add examples"` |
| [`ask`](#ask) | Quick Q&A (experimental) | `xunlong.py ask "What is AI?"` |
| [`status`](#status) | Check system status | `xunlong.py status` |

---

## `report` Command

Generate comprehensive research reports.

### Syntax

```bash
python xunlong.py report QUERY [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `QUERY` | Yes | Research topic or question |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--type` | `-t` | Choice | `comprehensive` | Report type |
| `--depth` | `-d` | Choice | `deep` | Search depth |
| `--max-results` | `-m` | Integer | `20` | Maximum search results |
| `--output-format` | `-o` | Choice | `html` | Output format |
| `--html-template` | | String | `academic` | HTML template |
| `--html-theme` | | String | `light` | HTML theme |
| `--verbose` | `-v` | Flag | `false` | Show detailed process |

### Report Types

| Value | Description | Best For |
|-------|-------------|----------|
| `comprehensive` | Full detailed report | In-depth analysis |
| `daily` | Daily briefing format | Quick updates |
| `analysis` | Analytical report | Data analysis |
| `research` | Academic research | Research papers |

### Search Depth

| Value | Speed | Results | Best For |
|-------|-------|---------|----------|
| `surface` | Fast | 5-10 | Quick overviews |
| `medium` | Moderate | 10-15 | Standard reports |
| `deep` | Slower | 15-20+ | Comprehensive research |

### Output Formats

| Value | Extension | Description |
|-------|-----------|-------------|
| `html` | `.html` | Styled web page |
| `md` / `markdown` | `.md` | Plain Markdown |

### HTML Templates

| Value | Style | Best For |
|-------|-------|----------|
| `academic` | Formal, structured | Research reports |
| `technical` | Code-friendly | Technical docs |

### HTML Themes

| Value | Style |
|-------|-------|
| `light` | Light background |
| `dark` | Dark background |

### Examples

**Basic usage:**
```bash
python xunlong.py report "Artificial Intelligence trends in 2025"
```

**Custom depth and results:**
```bash
python xunlong.py report "Blockchain technology" \
  --type analysis \
  --depth deep \
  --max-results 30
```

**Markdown output:**
```bash
python xunlong.py report "Quantum Computing" \
  -o md \
  -v
```

**Technical report with dark theme:**
```bash
python xunlong.py report "Kubernetes best practices" \
  --type research \
  --html-template technical \
  --html-theme dark
```

---

## `fiction` Command

Create fictional stories and novels.

### Syntax

```bash
python xunlong.py fiction QUERY [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `QUERY` | Yes | Story premise or description |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--genre` | `-g` | Choice | `mystery` | Story genre |
| `--length` | `-l` | Choice | `short` | Story length |
| `--viewpoint` | `-vp` | Choice | `first` | Narrative perspective |
| `--constraint` | `-c` | String | None | Special constraints (multi) |
| `--output-format` | `-o` | Choice | `html` | Output format |
| `--html-template` | | String | `novel` | HTML template |
| `--html-theme` | | String | `sepia` | HTML theme |
| `--verbose` | `-v` | Flag | `false` | Show details |

### Genres

| Value | Description | Characteristics |
|-------|-------------|-----------------|
| `mystery` | Mystery/Detective | Puzzle-solving, clues |
| `scifi` | Science Fiction | Futuristic, technology |
| `fantasy` | Fantasy | Magic, mythical |
| `horror` | Horror | Suspense, fear |
| `romance` | Romance | Love story |
| `wuxia` | Wuxia | Martial arts |

### Story Lengths

| Value | Chapters | Words | Reading Time |
|-------|----------|-------|--------------|
| `short` | 5 | 10,000-15,000 | 1-2 hours |
| `medium` | 12 | 30,000-50,000 | 3-5 hours |
| `long` | 30 | 80,000-120,000 | 8-12 hours |

### Viewpoints

| Value | Description | Example |
|-------|-------------|---------|
| `first` | First person | "I walked into the room..." |
| `third` | Third person limited | "She walked into the room..." |
| `omniscient` | Omniscient narrator | "Unknown to her, danger lurked..." |

### Constraints

Use `-c` multiple times to add constraints:

```bash
-c "locked room" -c "snowstorm" -c "limited time"
```

### HTML Templates

| Value | Style | Best For |
|-------|-------|----------|
| `novel` | Book-style layout | General fiction |
| `ebook` | E-reader optimized | Digital reading |

### HTML Themes

| Value | Background | Best For |
|-------|------------|----------|
| `light` | White | Day reading |
| `dark` | Black | Night reading |
| `sepia` | Cream | Eye comfort |

### Examples

**Basic mystery story:**
```bash
python xunlong.py fiction "A detective investigates a locked room murder"
```

**Sci-fi novella:**
```bash
python xunlong.py fiction "First contact with aliens" \
  --genre scifi \
  --length medium \
  --viewpoint third
```

**Constrained mystery:**
```bash
python xunlong.py fiction "Murder in a mansion" \
  --genre mystery \
  -c "snowstorm isolation" \
  -c "8 suspects" \
  -o html \
  -v
```

**Long fantasy epic:**
```bash
python xunlong.py fiction "Young hero's journey to save the kingdom" \
  --genre fantasy \
  --length long \
  --viewpoint omniscient \
  --html-template ebook
```

---

## `ppt` Command

Generate PowerPoint-style presentations.

### Syntax

```bash
python xunlong.py ppt TOPIC [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `TOPIC` | Yes | Presentation topic |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--style` | `-s` | Choice | `business` | PPT style |
| `--slides` | `-n` | Integer | `10` | Number of slides |
| `--depth` | `-d` | Choice | `medium` | Content depth |
| `--theme` | | String | `default` | Color theme |
| `--speech-notes` | | String | None | Generate speaker notes |
| `--verbose` | `-v` | Flag | `false` | Show details |

### PPT Styles

| Value | Description | Best For |
|-------|-------------|----------|
| `red` | RED minimalist | Simple, focused |
| `business` | Business detailed | Corporate |
| `academic` | Academic style | Research talks |
| `creative` | Creative design | Marketing |
| `simple` | Minimal design | Tech talks |

### Slide Counts

| Slides | Duration | Best For |
|--------|----------|----------|
| 5-7 | 5-10 min | Quick pitch |
| 10-15 | 15-20 min | Standard presentation |
| 20-30 | 30-45 min | Detailed talk |
| 40+ | 60+ min | Workshop/training |

### Depth Levels

| Value | Detail | Content/Slide |
|-------|--------|---------------|
| `surface` | Brief | 3-5 bullet points |
| `medium` | Balanced | 5-7 bullet points |
| `deep` | Detailed | 7-10 bullet points |

### Themes

| Value | Colors | Best For |
|-------|--------|----------|
| `default` | Neutral | General use |
| `blue` | Blue tones | Corporate |
| `red` | Red accent | Bold statements |
| `green` | Green tones | Environmental |
| `purple` | Purple shades | Creative |

### Speech Notes

Provide a scenario description to generate speaker notes:

```bash
--speech-notes "Investor pitch for seed funding"
```

This generates detailed talking points for each slide.

### Examples

**Basic presentation:**
```bash
python xunlong.py ppt "Artificial Intelligence Overview"
```

**Business presentation:**
```bash
python xunlong.py ppt "Q4 Sales Performance" \
  --style business \
  --slides 15 \
  --theme blue
```

**Academic talk:**
```bash
python xunlong.py ppt "Machine Learning Research" \
  --style academic \
  --depth deep \
  --slides 25
```

**Investor pitch with notes:**
```bash
python xunlong.py ppt "Startup Seed Round" \
  --style red \
  --slides 10 \
  --speech-notes "Presenting to venture capitalists" \
  -v
```

**Creative marketing deck:**
```bash
python xunlong.py ppt "New Brand Launch Campaign" \
  --style creative \
  --slides 18 \
  --theme purple \
  --depth medium
```

---

## `export` Command

Export projects to different formats.

### Syntax

```bash
python xunlong.py export PROJECT_ID --type FORMAT [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PROJECT_ID` | Yes | Project identifier (from generation output) |

### Options

| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--type` | `-t` | Choice | Yes | Export format |
| `--output` | `-o` | String | No | Custom output path |
| `--verbose` | `-v` | Flag | No | Show details |

### Export Formats

| Value | Extension | Description | Dependencies |
|-------|-----------|-------------|--------------|
| `pptx` | `.pptx` | PowerPoint file | `python-pptx` |
| `pdf` | `.pdf` | PDF document | `weasyprint` |
| `docx` | `.docx` | Word document | `python-docx` |
| `md` | `.md` | Markdown file | Built-in |

### Examples

**Export to PowerPoint:**
```bash
python xunlong.py export 20251005_143022_ai_trends --type pptx
```

**Export to PDF with custom path:**
```bash
python xunlong.py export 20251005_180344_report \
  --type pdf \
  --output ~/Desktop/my_report.pdf
```

**Export to Word:**
```bash
python xunlong.py export 20251005_215421_novel \
  --type docx \
  -v
```

**Export to Markdown:**
```bash
python xunlong.py export 20251005_123456_presentation --type md
```

### Install Export Dependencies

```bash
# For PPTX export
pip install python-pptx

# For PDF export
pip install weasyprint

# For DOCX export
pip install python-docx

# For Markdown conversion
pip install markdown2

# Install all
pip install python-pptx python-docx markdown2 weasyprint
```

---

## `iterate` Command

Refine and modify existing projects.

### Syntax

```bash
python xunlong.py iterate PROJECT_ID REQUIREMENT [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PROJECT_ID` | Yes | Project identifier |
| `REQUIREMENT` | Yes | Modification request |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verbose` | `-v` | Flag | `false` | Show details |

### Modification Examples

**For Reports:**
```bash
# Add content
python xunlong.py iterate 20251005_143022 "Add a section on future trends"

# Update data
python xunlong.py iterate 20251005_143022 "Update statistics with 2025 data"

# Improve clarity
python xunlong.py iterate 20251005_143022 "Simplify technical explanations"
```

**For Fiction:**
```bash
# Character development
python xunlong.py iterate 20251005_180344 "Make protagonist more conflicted in chapter 3"

# Plot enhancement
python xunlong.py iterate 20251005_180344 "Add foreshadowing in chapter 5"

# Pacing
python xunlong.py iterate 20251005_180344 "Slow down the climax scene"
```

**For PPT:**
```bash
# Add slides
python xunlong.py iterate 20251005_215421 "Add 2 slides on market analysis after slide 5"

# Modify content
python xunlong.py iterate 20251005_215421 "Change slide 3 chart to pie chart"

# Reorder
python xunlong.py iterate 20251005_215421 "Move conclusion before Q&A slide"
```

### Examples

**Add section to report:**
```bash
python xunlong.py iterate 20251005_143022 "Add case studies section"
```

**Enhance fiction chapter:**
```bash
python xunlong.py iterate 20251005_180344 "Rewrite chapter 5 with more suspense" -v
```

**Modify PPT slide:**
```bash
python xunlong.py iterate 20251005_215421 "Change slide 3 to use infographic" -v
```

---

## `ask` Command

Quick Q&A without deep research (experimental).

### Syntax

```bash
python xunlong.py ask QUESTION [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `QUESTION` | Yes | Your question |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--model` | `-m` | Choice | `balanced` | Model selection |
| `--verbose` | `-v` | Flag | `false` | Show details |

### Model Options

| Value | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `fast` | Fastest | Basic | Quick answers |
| `balanced` | Moderate | Good | General Q&A |
| `quality` | Slower | Best | Complex questions |

### Examples

```bash
# Basic question
python xunlong.py ask "What is quantum computing?"

# High quality answer
python xunlong.py ask "Explain machine learning" --model quality -v
```

**Note:** This feature is currently under development.

---

## `status` Command

Check system status and configuration.

### Syntax

```bash
python xunlong.py status
```

### Output Information

- System status
- LLM configuration count
- Available providers
- Provider status

### Example

```bash
python xunlong.py status
```

**Output:**
```
=== XunLong System Status ===

System: XunLong v1.0.0
Status: ✓ Running

LLM Configuration: 3 configs

Available Providers:
  • OpenAI: Available
  • Anthropic: Available
  • Local: Not configured
```

---

## Common Workflows

### 1. Generate Report → Export to PDF

```bash
# Step 1: Generate report
python xunlong.py report "AI Industry Analysis 2025" \
  --type comprehensive \
  --depth deep \
  -o md

# Step 2: Get project ID from output
# (e.g., 20251005_143022_ai_industry_analysis)

# Step 3: Export to PDF
python xunlong.py export 20251005_143022_ai_industry_analysis --type pdf
```

### 2. Create Fiction → Iterate → Export

```bash
# Step 1: Generate story
python xunlong.py fiction "Detective mystery" \
  --genre mystery \
  --length medium

# Step 2: Refine
python xunlong.py iterate 20251005_180344_detective_mystery \
  "Add more clues in chapter 3"

# Step 3: Export to DOCX
python xunlong.py export 20251005_180344_detective_mystery --type docx
```

### 3. Create PPT → Add Slides → Export

```bash
# Step 1: Generate PPT
python xunlong.py ppt "Product Launch 2025" \
  --style business \
  --slides 12

# Step 2: Add slides
python xunlong.py iterate 20251005_215421_product_launch \
  "Add 3 slides on pricing strategy"

# Step 3: Export to PowerPoint
python xunlong.py export 20251005_215421_product_launch --type pptx
```

---

## Environment Variables

Configure XunLong behavior via environment variables:

```bash
# LLM API Keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# LangFuse Tracking (optional)
export LANGFUSE_SECRET_KEY="your-key"
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"

# Default Settings
export XUNLONG_DEFAULT_DEPTH="deep"
export XUNLONG_DEFAULT_FORMAT="html"
```

---

## Tips & Best Practices

### 1. Use Verbose Mode for Debugging

```bash
python xunlong.py report "Topic" -v
```

Shows detailed execution steps.

### 2. Save Project IDs

Project IDs are needed for export and iteration:

```bash
# Good practice: save to variable
PROJECT_ID=$(python xunlong.py report "Topic" | grep "Project ID" | cut -d: -f2)
python xunlong.py export $PROJECT_ID --type pdf
```

### 3. Combine Formats

Generate both HTML and Markdown:

```bash
# Generate HTML
python xunlong.py report "Topic" -o html

# Export same project to Markdown
python xunlong.py export <project-id> --type md
```

### 4. Iterative Refinement

Don't aim for perfection on first try:

```bash
# 1. Quick generation
python xunlong.py report "Topic" --depth surface

# 2. Review output
# 3. Iterate to improve
python xunlong.py iterate <id> "Add more examples"
```

### 5. Use Appropriate Depth

| Task | Recommended Depth |
|------|-------------------|
| Quick overview | `surface` |
| Standard report | `medium` |
| Research paper | `deep` |
| Blog post | `surface` or `medium` |

---

## Troubleshooting

### Command Not Found

```bash
# Use python explicitly
python xunlong.py --help

# Or make executable
chmod +x xunlong.py
./xunlong.py --help
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install export dependencies
pip install python-pptx python-docx markdown2 weasyprint
```

### API Key Issues

```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Set API key
export OPENAI_API_KEY="sk-..."
```

### Project Not Found

```bash
# List projects
ls storage/

# Use full project ID including timestamp
python xunlong.py export 20251005_143022_full_name --type pdf
```

---

## Next Steps

- Learn about [Configuration](/api/configuration)
- Explore [Report Generation](/guide/features/report)
- Try [Fiction Writing](/guide/features/fiction)
- Check [PPT Creation](/guide/features/ppt)
