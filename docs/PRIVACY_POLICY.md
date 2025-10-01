# Privacy Policy

**Effective Date**: October 1, 2025
**Last Updated**: October 1, 2025

---

## 1. Introduction

Welcome to **XunLong Deep Search Agent System** ("we," "our," or "the System"). This Privacy Policy explains how we collect, use, store, and protect your information when you use our deep search and AI-powered research services.

By using XunLong, you agree to the collection and use of information in accordance with this policy.

---

## 2. Information We Collect

### 2.1 Information You Provide

When using XunLong, you may provide:

- **Search Queries**: The text queries you submit for deep search analysis
- **Configuration Data**: API keys, LLM provider settings, and system preferences stored in your local `.env` file
- **Feedback**: Any feedback, bug reports, or feature requests you submit

### 2.2 Automatically Collected Information

XunLong automatically collects and stores:

- **Search Results**: URLs, titles, and content extracted from web sources
- **Execution Logs**: Agent execution steps, timestamps, and processing metadata
- **Performance Metrics**: Search duration, token usage, and system performance data
- **Error Logs**: Error messages and stack traces for debugging purposes

### 2.3 Third-Party Data

XunLong integrates with third-party services:

- **LLM Providers** (DeepSeek, OpenAI, etc.): Query data sent for processing
- **Search Engines** (DuckDuckGo): Search queries submitted for results
- **Monitoring Services** (Langfuse, optional): Usage analytics and trace data
- **Web Content**: Publicly accessible web pages visited during content extraction

---

## 3. How We Use Your Information

### 3.1 Primary Uses

We use your information to:

- **Process Search Queries**: Execute deep search operations and generate reports
- **Store Results**: Save search projects, reports, and intermediate data locally
- **Improve Performance**: Optimize search algorithms and agent coordination
- **Provide Support**: Debug issues and respond to user inquiries

### 3.2 Local Storage

All search data is stored **locally** on your system in the `storage/` directory:

```
storage/
└── [project_id]/
    ├── metadata.json
    ├── intermediate/          # Processing steps
    ├── reports/               # Final reports
    └── search_results/        # Extracted content
```

**Important**: We do **not** transmit your stored search data to external servers unless you explicitly configure external monitoring services.

---

## 4. Data Sharing and Third-Party Services

### 4.1 LLM Providers

Your search queries and extracted content are sent to configured LLM providers (e.g., DeepSeek, OpenAI) for:
- Query analysis and task decomposition
- Content evaluation and synthesis
- Report generation

**Privacy Considerations**:
- Review your LLM provider's privacy policy
- Providers may store query data according to their terms
- Use providers compliant with your jurisdiction's data protection laws

### 4.2 Search Engines

Search queries are submitted to DuckDuckGo through Playwright browser automation:
- DuckDuckGo does not track users or store personal information
- Queries are sent over HTTPS connections
- No cookies or tracking pixels are retained

### 4.3 Web Content Extraction

XunLong extracts content from publicly accessible websites:
- Respects `robots.txt` directives
- Uses standard HTTP headers
- Does not bypass paywalls or authentication

### 4.4 Optional Monitoring (Langfuse)

If enabled, Langfuse collects:
- Trace data (execution steps, timing)
- Token usage metrics
- Query success/failure rates

**Note**: Monitoring is **optional** and can be disabled in configuration.

---

## 5. Data Retention

### 5.1 Local Storage

- **Project Data**: Stored indefinitely in `storage/` directory until manually deleted
- **Logs**: Rotated based on system configuration (default: 30 days)
- **Cache**: Cleared on system restart or manual cleanup

### 5.2 Third-Party Retention

- **LLM Providers**: Retention policies vary by provider (typically 30-90 days)
- **Langfuse**: Trace data retained according to your Langfuse plan settings

### 5.3 Data Deletion

To delete your data:

1. **Local Data**: Delete the corresponding project directory in `storage/`
2. **LLM Provider Data**: Contact your LLM provider directly
3. **Langfuse Data**: Use Langfuse dashboard to delete traces

---

## 6. Data Security

### 6.1 Security Measures

We implement the following security practices:

- **API Key Protection**: API keys stored in `.env` files excluded from version control
- **HTTPS Connections**: All external API calls use encrypted connections
- **Local Storage**: Data stored on your local file system with OS-level permissions
- **No Remote Database**: No centralized data collection or storage

### 6.2 User Responsibilities

You are responsible for:

- Securing your `.env` file and API keys
- Setting appropriate file system permissions
- Protecting your local `storage/` directory
- Reviewing third-party service privacy policies

### 6.3 Breach Notification

In the event of a data breach affecting third-party services:
- We will notify users within 72 hours
- Provide guidance on mitigation steps
- Coordinate with affected service providers

---

## 7. Children's Privacy

XunLong is **not intended for users under 13 years of age**. We do not knowingly collect personal information from children. If you believe a child has provided information, please contact us immediately.

---

## 8. Your Privacy Rights

Depending on your jurisdiction, you may have the following rights:

### 8.1 Access and Portability
- **Access**: View all stored search projects in `storage/` directory
- **Export**: All data stored in standard formats (JSON, Markdown, TXT)

### 8.2 Deletion
- **Right to Erasure**: Delete project directories at any time
- **Third-Party Deletion**: Request deletion from LLM providers

### 8.3 Rectification
- **Correct Data**: Edit `metadata.json` or regenerate reports

### 8.4 Object to Processing
- **Disable Features**: Turn off monitoring or specific agents in configuration

### 8.5 Data Portability
- All data stored in open formats (JSON, Markdown)
- Easy to export and transfer to other systems

---

## 9. International Data Transfers

### 9.1 Cross-Border Data Flow

If you use LLM providers located outside your country:
- Data may be transferred to servers in other jurisdictions
- Ensure your provider complies with applicable data protection laws (GDPR, CCPA, etc.)

### 9.2 Recommended Practices

For EU users:
- Use LLM providers with GDPR compliance
- Enable data residency options when available
- Review provider's Standard Contractual Clauses (SCCs)

---

## 10. Cookies and Tracking

### 10.1 No Tracking Cookies

XunLong does **not** use cookies or tracking technologies in its core functionality.

### 10.2 Browser Automation

Playwright browser automation:
- Runs in headless mode
- Does not persist cookies between sessions
- Does not track user behavior

---

## 11. Changes to This Privacy Policy

We may update this Privacy Policy periodically. Changes will be:

- Posted on this page with an updated "Last Updated" date
- Significant changes will be highlighted in the changelog
- Continued use after changes constitutes acceptance

**Changelog**:
- **2025-10-01**: Initial privacy policy published

---

## 12. Legal Compliance

### 12.1 GDPR Compliance (EU Users)

Under GDPR, you have rights to:
- Access your data
- Request deletion
- Object to processing
- Data portability

**Legal Basis**: Legitimate interest and user consent

### 12.2 CCPA Compliance (California Users)

Under CCPA, you have rights to:
- Know what data is collected
- Request deletion
- Opt-out of data sales (N/A - we don't sell data)

### 12.3 Other Jurisdictions

We comply with applicable data protection laws in:
- Canada (PIPEDA)
- Australia (Privacy Act 1988)
- Other jurisdictions as required

---

## 13. Third-Party Links

XunLong extracts content from third-party websites. We are not responsible for:
- Privacy practices of external websites
- Content accuracy or legality
- Third-party terms of service

Always review privacy policies of websites you visit.

---

## 14. Open Source and Transparency

XunLong is open source software:
- Source code available for audit
- Community contributions welcome
- Transparency in data handling practices

**Repository**: [GitHub Repository URL]

---

## 15. Contact Us

If you have questions about this Privacy Policy or data handling:

**Email**: [Contact Email]
**GitHub Issues**: [Repository Issues URL]
**Documentation**: See `docs/` directory

---

## 16. Disclaimer

### 16.1 No Warranty

XunLong is provided "as is" without warranties of any kind. We do not guarantee:
- Accuracy of search results
- Availability of third-party services
- Data integrity or security

### 16.2 Limitation of Liability

We are not liable for:
- Loss or corruption of stored data
- Third-party service failures
- Unauthorized access to your system
- Misuse of extracted content

### 16.3 User Responsibility

You are responsible for:
- Compliance with applicable laws
- Proper use of search results
- Respecting copyright and intellectual property
- Securing your system and API keys

---

## 17. Acceptable Use

When using XunLong, you agree to:

✅ **Allowed**:
- Personal research and information gathering
- Academic and educational purposes
- Business intelligence and market research
- Content analysis and synthesis

❌ **Prohibited**:
- Illegal activities or prohibited content
- Harassment, spam, or malicious use
- Circumventing website access controls
- Copyright infringement
- Automated scraping at scale without permission

---

## 18. Summary

**What We Collect**:
- Search queries and results (stored locally)
- Execution logs and performance metrics
- Configuration data (API keys, settings)

**How We Use It**:
- Process searches and generate reports
- Improve system performance
- Debug issues and provide support

**How We Protect It**:
- Local storage only (no remote database)
- HTTPS for all external connections
- API keys excluded from version control
- Open source for transparency

**Your Rights**:
- Access and export all data
- Delete data at any time
- Control third-party integrations
- Disable monitoring features

**Third-Party Services**:
- LLM providers (query processing)
- DuckDuckGo (search results)
- Langfuse (optional monitoring)

---

## 19. Acknowledgment

By using XunLong Deep Search Agent System, you acknowledge that you have read, understood, and agree to be bound by this Privacy Policy.

If you do not agree with this policy, please discontinue use of the System.

---

**XunLong Deep Search Agent System**
**Version**: 2.0
**Privacy Policy Version**: 1.0
**Effective Date**: October 1, 2025

---

*For the most up-to-date version of this Privacy Policy, please refer to the documentation in the `docs/` directory.*
