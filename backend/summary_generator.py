import validators
from openai import OpenAI
import openai
import time

class Summary_gen:
    #Summary Generation using openapi, can be called prior to addition to graph
    #No need for deconstructor as python garbage collection will handle
    #Necessary libraries: openapi, validators
    """
    Initialise variables and call function to fetch summary
    @params str.request:url to fetch summary for
    @outputs str.out:fetched summary
    """
    def __init__(self, request) -> str:
        self.request = request
        self.client = OpenAI(
            # defaults to os.environ.get("OPENAI_API_KEY")
            api_key="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",
        )

    """
    Call openapi to fetch summary
    @params str.request:url to fetch summary for
    @outputs str.response:fetched summary
    """
    def generate_summary(self) -> str:
        max_retries = 5 
        delay = 2 
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful academic research assistant."},
                        {"role": "user", "content": f"Summarize the following academic paper:\n\n{self.request}"}
                    ],
                    max_tokens=400
                )
                print(response)
                self.summary = response.choices[0].message.content.strip()
                return self.summary
            except openai.error.RateLimitError as e:
                print(f"Rate limit exceeded: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2 
                else:
                    return "Rate limit exceeded. Please try again later."
            except openai.error.OpenAIError as e:
                print(f"An error occurred: {e}")
                return "An error occurred. Please try again later."

        return "Failed to generate summary after multiple attempts due to rate limiting."
    
    # Call summary generator if url is validated by validators library
    def fetch_sum(self):
        if validators.url(self.request):
            out = self.generate_summary()
        else:
            out = "invalid URL detected, please try again"
        return out
