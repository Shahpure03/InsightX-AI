"""Tool to categorize text intelligently based on full content context."""

from tools.llm import call_groq

VALID_CATEGORIES = [
    "AI & Future", "Tech Innovation", "Startups", "Science", "Global Trends", 
    "Sports", "Entertainment", "Lifestyle", "Education", "Economy", "Careers", "Politics"
]

async def categorize_by_content(title: str, content: str) -> str:
    """
    Categorizes the article by prompting the LLM to understand semantic context 
    instead of relying on strict keyword matching.
    """
    system = "You are an expert news classifier."
    prompt = f"""
Analyze the context, tone, and actual subject matter of the following news article. 
Do not rely blindly on keywords. Understand the entity's core topic.

Assign it strictly to ONE of the matching categories below:
{', '.join(VALID_CATEGORIES)}

Respond with ONLY the exact string from the list above. No explanations.

Title: {title}
Content: {content[:1500]}
"""
    
    result = await call_groq(prompt, system)
    
    # Secure string matching to prevent Hallucinations breaking the pill formatting
    for category in VALID_CATEGORIES:
        if category.lower() in result.lower():
            return category
            
    return "Global Trends"
