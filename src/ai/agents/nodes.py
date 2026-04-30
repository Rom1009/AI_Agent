import os
from langchain_ollama import ChatOllama
from src.ai.agents.state import DigestState
from ddgs import DDGS
from html import escape
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.message import EmailMessage
from langchain_groq import ChatGroq
from src.ai.agents.datatype import SearchQueries, ScoreOutput
import yaml
from src.utils.logger import setup_logger
from src.utils.config import settings
from src.db.db import is_already_sent, add_to_history
from src.app.schema.model import Article, User, Joblog

logger = setup_logger("AgentNode")

llm = ChatGroq(model=settings.MODEL_NAME, api_key=settings.GROQ_API_KEY, max_tokens=1000)

def load_config(state: DigestState) -> dict:

    config_path = settings.CONFIG_PATH
    logger.info(f"Loading configuration from {config_path}")

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at {config_path}")
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    
    data = data["input"]
    return {
        "user_id": data.get("user_id", "default_user"),
        "run_date": data.get("run_date", datetime.now().strftime("%Y-%m-%d")),
        "topics": data.get("topics", []),
        "max_articles_per_topic": data.get("max_articles_per_topic", 3),
        "user_interests": data.get("user_interests", []),
        "output_language": data.get("output_language", "en"),
        "digest_style": data.get("digest_style", "brief")

    }

def load_profile(state: DigestState) -> dict:
    logger.info(f"Loading user profile for user_id: {state['user_id']}")
    topics = state["topics"] or ["RAG"]
    max_articles = state["max_articles_per_topic"] or 2

    logger.info(f"User profile loaded with topics: {topics} and max_articles_per_topic: {max_articles}")
    return {
        "topics": topics,
        "max_articles": max_articles
    }

def generate_queries(state: DigestState) -> dict:
    logger.info(f"Generating search queries based on topics: {state['topics']}")
    topics = state["topics"]
    prompt = f"""
        Role: 
        You are an planner expert. 

        Task: 
        Generate exactly 2 search queries for the given topics 

        Topics:
        {topics}

        Rules: 
        -  One general query
        - One more specific or technical query
        - Each query must be short
        - Include one keyword: latest, news, update, or release notes
        - Do not generate more than 2 queries

        OutputJson:
        {{
            "queries": ["...", "..."]
        }}

    """

    llm_with_tool = llm.with_structured_output(SearchQueries)
    logger.info(f"Invoking LLM to generate queries with prompt: {prompt}")
    response = llm_with_tool.invoke(prompt)
    logger.info(f"Received response from LLM: {response}")

    return {
        "queries": response.queries
    }
    
def web_search(state: DigestState) -> dict:
    logger.info(f"Performing web search for queries: {state['queries']}")
    queries = state["queries"]
    results = []

    search = DDGS()
    for query in queries:
        logger.info(f"Searching for query: {query}")
        search_results = list(search.text(query, max_results=state["max_articles_per_topic"]))

        logger.info(f"Found {len(search_results)} results for query: {query}")
        results.append({
            "query": query,
            "results": search_results
        })

    return {"candidate_urls": results}

def filter_nodes(state: DigestState) -> dict:
    logger.info("Filtering candidate URLs based on relevance to user interests")

    new_articles = []

    for candidate in state["candidate_urls"]:
        query = candidate["query"]
        results = candidate["results"]
        for result in results:
            url = result.get("href", "")
            title = result.get("title", "")
            body = result.get("body", "")

            article = Article(url = url, title = title)

            if not is_already_sent(url):
                logger.info(f"New article found: {title} ({url})")
                new_articles.append({
                    "query": query,
                    "title": title,
                    "body": body,
                    "src_url": url
                })
                add_to_history(article)
    
    return {"filtered_aricles": new_articles}

def filter_docs(state: DigestState) -> dict: 
    logger.info(f"Filtering documents based on relevance to user interests: {state.get('user_interests', 'General Technology and AI')}")
    filtered_aricles = state["filtered_aricles"]
    filtered_results = []
    llm_with_tool = llm.with_structured_output(ScoreOutput)
    for candidate in filtered_aricles:
        query = candidate["query"]
        title = candidate["title"]
        body = candidate["body"]

        logger.info(f"Processing document: {title}")
        logger.debug(f"Document content snippet: {body[:200]}")  # Log the first 200 characters of the body for debugging
        content_snippet = body[:1200] 

        prompt = f"""
            Role: Professional News Analyst
            Task: Evaluate the relevance of the news article below to the user's specific interests.
            
            User Interests: {state.get('user_interests', 'General Technology and AI')}
            Search Context: This article was found using the query "{query}".

            Article Title: {title}
            Article Content: {content_snippet}

            Rules:
            1. Analyze the relationship between the article and the User Interests.
            2. Provide a relevance score from 1 (irrelevant) to 10 (perfect match).
            3. High scores (7+) should be reserved for articles that directly impact or provide deep insight into the user's topics.
            4. Focus only on content relevance, ignoring writing style or source.
        """

        try: 
            logger.info(f"Invoking LLM to score document relevance with prompt: {prompt}")
            response = llm_with_tool.invoke(prompt)
            logger.info(f"Relevance analysis for '{title}': Score {response.score}, Analysis: {response.analysis}")
            if response.score >=7: 
                filtered_results.append({
                    "query": query,
                    "title": title,
                    "body": body,
                    "src_url": candidate["src_url"],
                    "analysis": response.analysis,
                    "score": response.score
                })
        except Exception as e:
            logger.error(f"Error scoring document relevance: {e}")
            raise RuntimeError(f"Error scoring document relevance: {e}")

    return {
        "filtered_docs": filtered_results
    }

def summarize_with_llm(state: DigestState) -> dict:
    logger.info(f"Summarizing {len(state['filtered_docs'])} documents with LLM")
    docs = state["filtered_docs"]
    summaries = []
    for doc in docs:
        prompt = f"""
        Summarize the following content for a morning email digest.

        Rules:
        - Maximum 3 bullet points
        - Each bullet must be one short sentence
        - Focus only on what is new or important
        - No introduction like "Here's a summary"
        - No repetition
        - Keep it compact and professional

        Content:
        {doc['body']}
        """ 
        summary = llm.invoke(prompt)
        logger.info(f"Received summary from LLM for '{doc['title']}': {summary}")
        summary_text = summary.content if hasattr(summary, "content") else str(summary)
        logger.debug(f"Summary text for '{doc['title']}': {summary_text}")

        summaries.append({
            "query": doc["query"],
            "title": doc["title"],
            "summary": summary_text,
            "src_url": doc["src_url"]
        })
    return {"summarized_docs": summaries}

def convert_to_markdown(state: DigestState) -> dict:
    logger.info(f"Converting summarized documents to markdown format for email body")
    summarizes = state["summarized_docs"]

    lines = ["# Morning Digest", ""]
    logger.info(f"Generating markdown for {len(summarizes)} summarized documents")
    for item in summarizes:
        lines.append(f"## {item['query']}")
        lines.append(f"### {item['title']}")
        lines.append(f"{item['summary']}")
        lines.append(f"[Read more]({item['src_url']})")
        lines.append("")
    
    markdown = "\n".join(lines).strip() or "# Morning Digest\n\nNo content available."
    logger.debug(f"Generated markdown content:\n{markdown}")
    return {
        "email_markdown": markdown,
    }


def render_bullets(summary_text: str) -> str:
    logger.info(f"Rendering summary text into HTML bullets")
    lines = str(summary_text).split("\n")
    items = []
    logger.debug(f"Summary text split into {len(lines)} lines for bullet rendering")
    for line in lines:
        cleaned = line.strip().lstrip("-*+ ").strip()
        if cleaned:
            items.append(
                f"<li style='margin-bottom:10px; color:#374151; line-height:1.65;'>{escape(cleaned)}</li>"
            )
    
    if not items:
        return "<p style='color:#6b7280;'>No summary available.</p>"

    return f"<ul style='padding-left:20px; margin:12px 0 0 0;'>{''.join(items)}</ul>"


def build_email_html(summaries, topics=None):
    logger.info(f"Building HTML content for email with {len(summaries)} summaries and topics: {topics}")
    today = datetime.now().strftime("%d %b %Y")
    topic_text = ", ".join(topics or [])

    html_parts = [
        """
        <html>
          <body style="margin:0; padding:0; background:#f3f4f6; font-family: Inter, Arial, Helvetica, sans-serif;">
            <div style="max-width:760px; margin:0 auto; padding:32px 20px;">
              <div style="background:#111827; color:white; padding:28px 32px; border-radius:18px 18px 0 0;">
                <div style="font-size:13px; letter-spacing:0.08em; text-transform:uppercase; opacity:0.75;">
                  Personalized Morning Research Agent
                </div>
                <h1 style="margin:10px 0 8px 0; font-size:30px; line-height:1.2;">
                  Morning Digest
                </h1>
        """
    ]

    html_parts.append(
        f"""
                <p style="margin:0; font-size:15px; color:#d1d5db;">
                  Daily brief for <strong>{escape(topic_text) if topic_text else 'your selected topics'}</strong>
                </p>
              </div>

              <div style="background:white; padding:28px 32px; border-radius:0 0 18px 18px; box-shadow:0 10px 30px rgba(0,0,0,0.06);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; flex-wrap:wrap; gap:8px;">
                  <div style="font-size:14px; color:#6b7280;">{today}</div>
                  <div style="font-size:13px; color:#9ca3af;">Auto-generated research summary</div>
                </div>

                <div style="margin-bottom:24px; padding:16px 18px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px;">
                  <div style="font-size:14px; color:#374151; line-height:1.7;">
                    Curated highlights from web sources, summarized into a compact morning brief.
                  </div>
                </div>
        """
    )

    for idx, item in enumerate(summaries, start=1):
        query = escape(str(item.get("query", "Untitled Topic")))
        title = escape(str(item.get("title", "No Title")))
        source_url = escape(str(item.get("src_url", "#")))
        summary_text = item.get("summary", "")
        if hasattr(summary_text, "content"):
            summary_text = summary_text.content

        bullets_html = render_bullets(summary_text)

        logger.info(f"Adding summary to email HTML for topic '{query}' with title '{title}'")
        logger.debug(f"Summary text for HTML rendering:\n{summary_text}")
        logger.debug(f"Generated bullets HTML:\n{bullets_html}")

        html_parts.append(
            f"""
                <div style="margin-top:26px; border:1px solid #e5e7eb; border-radius:16px; overflow:hidden;">
                  <div style="padding:16px 20px; background:#fafafa; border-bottom:1px solid #e5e7eb;">
                    <div style="font-size:12px; color:#9ca3af; text-transform:uppercase; letter-spacing:0.08em;">
                      Topic: {idx}
                    </div>
                    <h2 style="margin:8px 0 0 0; font-size:22px; color:#111827; line-height:1.3;">
                      {query}
                    </h2>
                    <p style="margin:6px 0 0 0; font-size:14px; color:#6b7280;">
                      {title}
                    </p>

                  </div>

                  <div style="padding:18px 20px 20px 20px;">
                    {bullets_html}

                    <div style="margin-top:18px;">
                      <a href="{source_url}"
                         style="display:inline-block; padding:10px 14px; background:#111827; color:#ffffff; text-decoration:none; border-radius:10px; font-size:14px; font-weight:600;">
                        Read source
                      </a>
                    </div>
                  </div>
                </div>
            """
        )

    html_parts.append(
        """
                <div style="margin-top:30px; padding-top:18px; border-top:1px solid #e5e7eb;">
                  <p style="margin:0; font-size:12px; color:#9ca3af; line-height:1.7;">
                    Generated by your AI research workflow using LangGraph + FastAPI.
                  </p>
                </div>
              </div>
            </div>
          </body>
        </html>
        """
    )

    return "".join(html_parts)


def format_email(state: DigestState) -> dict:
    logger.info(f"Formatting email content based on summarized documents and topics")   
    topics = state.get("topics", [])
    subject = f"Morning Digest | {', '.join(topics)}"

    html_body = build_email_html(
        summaries=state.get("summarized_docs", []),
        topics=topics
    )

    logger.debug(f"Formatted email subject: {subject}")
    logger.debug(f"Formatted email HTML body:\n{html_body}")
    return {
        "email_subject": subject,
        "email_html": html_body,
        "email_markdown": state.get("email_markdown", "")
    }

def clean_text(text: str) -> str:
    if not text:
        return ""
    return (
        str(text)
        .replace("\xa0", " ")
        .replace("\u200b", "")
        .strip()
    )

def send_email(state: DigestState):
    logger.info(f"Preparing to send email with subject: {state.get('email_subject', 'No Subject')}")
    # 1. Thông tin cấu hình (Nên để trong biến môi trường .env)
    sender_email = settings.MAIL_SENDER
    receiver_email = settings.MAIL_RECEIVER
    password = settings.MAIL_PASSWORD.get_secret_value()

    # 2. Lấy nội dung từ State
    subject = clean_text(state["email_subject"])
    plain_body = clean_text(state["email_markdown"])
    html_body = state["email_html"]


    # 3. Tạo cấu trúc Email
    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = str(Header(subject, "utf-8"))
    # message.attach(MIMEText(body, "plain", "utf-8"))
    message.set_content(plain_body, subtype="plain", charset="utf-8") 
    message.add_alternative(html_body, subtype="html", charset="utf-8") 


    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(message)
        logger.info(f"Email sent successfully to {receiver_email} with subject: {subject}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

    return state #