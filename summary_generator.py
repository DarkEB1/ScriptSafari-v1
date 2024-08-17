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
        openai.api_key = 'enter_openapi_key'
        if validators.ur(request)
            out = generate_summary(request)
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
        return response.choices[0].text.strip()