from openai import OpenAI
import PyPDF2


def generate_text(prompt: str) -> str:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    return completion.choices[0].message.content


def read_text_from_pdf(path: str) -> str:
    with open(path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


if __name__ == "__main__":
    print(generate_text("Hello, world!"))
