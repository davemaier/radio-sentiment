import marimo

__generated_with = "0.3.12"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    from openai import OpenAI
    return OpenAI, mo


@app.cell
def __(mo):
    mo.md(
    """
    # Transcript analysis

    This script can be used to analyze a transcript of a radioshow (or any other text). It uses **OpenAIs GPT4-turbo** model via the provides API. To make communication with the API more compfortable, we use the official OpenAI Python SDK. 
    """
    )
    return


@app.cell
def __(OpenAI):
    client = OpenAI(
      organization='org-wTkHlf3xgp0VhSI8oNBaLSqO'
    )
    return client,


@app.cell
def __(client):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say hi!"}]
    )

    print(response.choices.pop().message.content)


    return response,


if __name__ == "__main__":
    app.run()
