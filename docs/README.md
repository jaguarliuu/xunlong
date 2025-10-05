# XunLong Documentation

This directory contains the VitePress documentation site for XunLong.

## Development

### Install Dependencies

```bash
cd docs
npm install
```

### Run Dev Server

```bash
npm run docs:dev
```

The documentation site will be available at http://localhost:5173

### Build for Production

```bash
npm run docs:build
```

### Preview Production Build

```bash
npm run docs:preview
```

## Project Structure

```
docs/
├── .vitepress/
│   ├── config.mts          # VitePress configuration
│   └── cache/              # Build cache (gitignored)
├── public/                 # Static assets
│   └── icon.png
├── guide/                  # English guides
│   ├── getting-started.md
│   ├── architecture.md
│   └── ...
├── zh/                     # Chinese documentation
│   ├── guide/
│   └── index.md
├── index.md                # English homepage
└── package.json

```

## Writing Documentation

### Markdown Features

VitePress supports extended Markdown features:

- **Mermaid Diagrams** - Embedded flowcharts and diagrams
- **Code Blocks** with syntax highlighting
- **Custom Containers** (tip, warning, danger, etc.)
- **Tables** and **Emojis**
- **Internal Links** with automatic `.md` -> `.html` conversion

### Adding New Pages

1. Create a new `.md` file in the appropriate directory
2. Add the page to the sidebar configuration in `.vitepress/config.mts`
3. Write your content using Markdown

### Example: Custom Container

```markdown
::: tip
This is a tip
:::

::: warning
This is a warning
:::

::: danger
This is a dangerous warning
:::
```

## Deployment

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `master` branch.

See `.github/workflows/deploy-docs.yml` for the deployment configuration.

## License

MIT
