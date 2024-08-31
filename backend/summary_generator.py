import validators
import openai

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
        openai.api_key = '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'
        if validators.ur(request):
            out = self.generate_summary(request)
        else:
            out = "invalid URL detected, please try again"
        return out
        

    """
    Call openapi to fetch summary
    @params str.request:url to fetch summary for
    @outputs str.response:fetched summary
    """
    def generate_summary(self) -> str:
        response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following academic paper:\n\n{self.request}",
        max_tokens=200
        )
        self.summary = response.choices[0].text.strip()
        return response.choices[0].text.strip()
    
    