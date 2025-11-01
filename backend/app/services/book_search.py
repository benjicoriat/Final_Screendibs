from groq import Groq
import json
from typing import List, Optional
from ..core.config import settings
from ..models.schemas import BookInfo

class BookSearchService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def search_books(
        self, 
        description: str, 
        additional_details: Optional[str] = None,
        exclude_titles: List[str] = []
    ) -> List[BookInfo]:
        """Search for 10 books matching the criteria."""
        
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
                        "content": "You are a helpful librarian assistant who provides accurate book recommendations in JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            books_data = json.loads(content)
            
            # Convert to BookInfo objects
            books = [BookInfo(**book) for book in books_data]
            
            return books
            
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing AI response: {e}")
        except Exception as e:
            raise Exception(f"Error searching books: {e}")