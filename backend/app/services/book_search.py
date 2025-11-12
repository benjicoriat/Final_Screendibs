import json
import logging
import re
import time
from typing import List, Optional

from groq import Groq

from ..core.config import settings
from ..models.schemas import BookInfo

logger = logging.getLogger(__name__)


class BookSearchService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            logger.warning("GROQ_API_KEY not configured; using fallback book recommendations.")
            self.client = None
        self.max_retries = 3
        self.base_backoff = 1  # seconds

    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter."""
        import random

        delay = self.base_backoff * (2**attempt) + random.uniform(0, 1)
        result: float = min(delay, 30)  # Cap at 30 seconds
        return result

    def search_books(
        self, description: str, additional_details: Optional[str] = None, exclude_titles: List[str] = []
    ) -> List[BookInfo]:
        """Search for 10 books matching the criteria with retries."""

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Book search attempt {attempt + 1}/{self.max_retries} for: {description[:50]}...")
                return self._do_search(description, additional_details, exclude_titles)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Book search failed after {self.max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Book search error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise
        return []

    def _do_search(
        self, description: str, additional_details: Optional[str], exclude_titles: List[str]
    ) -> List[BookInfo]:
        """Internal method to perform the actual search."""

        if self.client is None:
            return self._fallback_results(description)

        prompt = f"""You are a knowledgeable librarian assistant. Find exactly 10 books that match the following criteria:

PRIMARY CRITERIA: {description}
ADDITIONAL DETAILS: {additional_details if additional_details else "No additional constraints"}

For each book, provide:
1. Title (exact, official title)
2. Author(s) (full name(s))
3. Publication year (original publication date)
4. Genre/Type (e.g., thriller, biography, sci-fi, mystery, romance, fantasy, historical fiction, horror, non-fiction, memoir, etc.)
5. Description (exactly 2 sentences that synthesize the book's plot, themes, or main content - NOT why it matches the criteria)

Format your response as a valid JSON array with this exact structure:
[
    {{
        "title": "Book Title",
        "author": "Author Name",
        "year": "YYYY",
        "type": "genre/type",
        "description": "First sentence about the book. Second sentence about the book."
    }}
]

IMPORTANT: 
- Only include real, published books
- Provide accurate publication dates and genres
- The description must be a synthesis of the book itself (plot, themes, content), not an explanation of why it matches the search
- Each description must be exactly 2 complete sentences
- Ensure variety in your selections
- Avoid books already suggested: {exclude_titles if exclude_titles else 'None yet'}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful librarian assistant who provides accurate book recommendations in JSON format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2000,
            )

            content = response.choices[0].message.content.strip()
            logger.debug(f"LLM response length: {len(content)} chars")

            # Clean up JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Try direct JSON parse first; if that fails, attempt to extract a JSON array using regex
            try:
                books_data = json.loads(content)
            except json.JSONDecodeError:
                # conservative regex to extract the first JSON array-looking substring
                m = re.search(r"(\[\s*\{.*?\}\s*\])", content, re.S)
                if m:
                    try:
                        books_data = json.loads(m.group(1))
                    except json.JSONDecodeError as e:
                        raise Exception(f"Error parsing AI response (extracted): {e}\nContent: {m.group(1)[:200]}")
                else:
                    raise Exception(f"Error parsing AI response: invalid JSON. Raw content: {content[:500]}")

            # Convert to BookInfo objects, coerce year to string
            books = []
            for book in books_data:
                # Ensure keys are strings and year is string
                if "year" in book and not isinstance(book["year"], str):
                    book["year"] = str(book["year"])
                books.append(BookInfo(**book))

            logger.info(f"Successfully retrieved {len(books)} books")
            return books

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Book search service error: {e}")
            raise

    def _fallback_results(self, description: str) -> List[BookInfo]:
        """Return deterministic placeholder results when the Groq API key is missing."""

        topic = description.strip() or "Curated Reads"
        base_title = topic.title() if len(topic) < 60 else topic[:57].title() + "..."

        placeholders = [
            BookInfo(
                title=f"{base_title} Anthology",
                author="Screendibs Research Team",
                year="2024",
                type="Reference",
                description="An accessible overview compiled by the Screendibs team. A real Groq API key unlocks live book discovery.",
            ),
            BookInfo(
                title=f"Exploring {base_title}",
                author="Screendibs Research Team",
                year="2024",
                type="Guide",
                description="A concise guide inspired by your search topic. Enable Groq integration to receive ten tailored literary recommendations.",
            ),
            BookInfo(
                title=f"{base_title} Essentials",
                author="Screendibs Research Team",
                year="2024",
                type="Overview",
                description="Key themes and reading paths curated as a temporary stand-in. Configure GROQ_API_KEY for AI-powered suggestions.",
            ),
        ]

        logger.info("Provided fallback book results; configure GROQ_API_KEY for live recommendations.")
        return placeholders
