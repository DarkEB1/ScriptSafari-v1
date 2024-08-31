import validators
from openai import OpenAI

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
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful academic research assistant."},
                {"role": "user", "content": f"Summarize the following academic paper:\n\n{self.request}"}
            ],
            max_tokens=200
        )
        print(response)
        self.summary = response['choices'][0]['message']['content'].strip()
        return self.summary
    
    def fetch_sum(self):
        if validators.url(self.request):
            out = self.generate_summary()
        else:
            out = "invalid URL detected, please try again"
        return out
