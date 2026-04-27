# Personalized Morning Research Agent

A sophisticated AI-powered agent built with LangGraph that automates the creation and delivery of personalized morning research digests via email. This system leverages large language models to curate, summarize, and format relevant news and updates based on user-specified topics and interests.

## Features

- **Intelligent Query Generation**: Automatically generates targeted search queries (general and technical) for given topics using LLM-powered planning.
- **Web Search Integration**: Performs web searches using DuckDuckGo Search API to gather candidate articles.
- **Content Filtering**: Uses AI to score and filter articles based on relevance to user interests, ensuring only high-quality content (score ≥7/10) is included.
- **Smart Summarization**: Summarizes filtered articles into concise bullet points, focusing on key insights and updates.
- **Email Formatting**: Generates both Markdown and HTML email formats with professional styling.
- **Automated Email Delivery**: Sends formatted digests via Gmail SMTP with proper encoding and multipart support.
- **Modular Architecture**: Built as a LangGraph state machine for easy extension and debugging.
- **Configurable**: Supports multiple topics, user interests, languages, and digest styles.

## Architecture

The agent follows a sequential workflow implemented as a directed graph:

1. **Load Profile**: Initializes user preferences and settings.
2. **Generate Queries**: Creates 2 targeted search queries per topic.
3. **Web Search**: Retrieves articles from web sources.
4. **Filter Documents**: Scores and filters articles for relevance.
5. **Summarize**: Generates concise summaries using LLM.
6. **Format Email**: Creates Markdown and HTML email content.
7. **Send Email**: Delivers the digest via email.

## Technologies Used

- **LangGraph**: For building the agent workflow and state management.
- **LangChain**: Integration with LLMs and structured outputs.
- **Groq API**: Fast LLM inference for query generation, filtering, and summarization.
- **DuckDuckGo Search (ddgs)**: Privacy-focused web search.
- **Pydantic**: Data validation and structured outputs.
- **Email Libraries**: smtplib, email.message for SMTP and email formatting.
- **Jupyter Notebook**: Development and testing environment.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agent
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file with:
   ```
   GROQ_API_KEY=your_groq_api_key
   MAIL=your_gmail_address
   PASS_WORD_MAIL=your_gmail_app_password
   ```

## Usage

### Running the Agent

1. **Open the Jupyter notebook**:
   ```bash
   jupyter notebook notebook/test.ipynb
   ```

2. **Configure initial state**:
   Modify the `initial_state` dictionary with your preferences:
   ```python
   initial_state = {
       "user_id": "your_user_id",
       "run_date": "2026-04-27",
       "topics": ["Computer Vision", "AI Research"],
       "max_articles_per_topic": 3,
       "user_interests": ["CNN", "YOLO", "Transformers"],
       "output_language": "en",
       "digest_style": "brief",
       # ... other fields
   }
   ```

3. **Execute the graph**:
   ```python
   result = graph.invoke(initial_state)
   ```

### Docker Deployment

The project includes Docker support for containerized deployment:

```bash
docker-compose up --build
```

## Configuration

### State Parameters

- `user_id`: Unique identifier for the user.
- `topics`: List of topics to research (e.g., ["Computer Vision"]).
- `max_articles_per_topic`: Number of articles to retrieve per query.
- `user_interests`: Specific interests for relevance filtering.
- `output_language`: Language for the digest (currently supports "en", "vi").
- `digest_style`: Style of the digest ("brief").

### Email Configuration

- Uses Gmail SMTP (smtp.gmail.com:465) with SSL.
- Requires app-specific password for Gmail accounts.
- Supports both plain text and HTML email formats.

## Example Output

The agent generates professional email digests with:

- **Subject**: "Morning Digest | Computer Vision"
- **HTML Body**: Styled email with topic sections, article summaries, and source links.
- **Markdown Body**: Plain text version for compatibility.

Sample email structure:
```
Morning Digest

## Computer Vision latest news
### Article Title
- Key point 1
- Key point 2
- Key point 3
[Read more](source_url)
```

## Development

### Project Structure

```
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker configuration
├── notebook/
│   └── test.ipynb         # Main development notebook
├── agents/                 # Agent-related modules
├── data/                   # Data storage
├── tools/                  # Utility tools
└── mcp_servers/           # MCP server configurations
```

### Extending the Agent

- Add new nodes to the graph for additional processing steps.
- Integrate different LLMs or search providers.
- Implement user feedback loops or personalization features.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with LangGraph for robust agent workflows
- Powered by Groq for fast LLM inference
- Inspired by automated research and content curation systems 