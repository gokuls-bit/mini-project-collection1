from openai import OpenAI
client = OpenAI(
   #api_key = os.environ.get("OPENAI_API_KEY")
   api_key = "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",
      )
completion =  client.chat.completions.create(
   model = "gpt-3.5-turbo",
   messages = [
    {"role": "system", "content": "You are a poetic assistant , skilled in explaining complex programming concepts with creative flair."},
    {"role":"user","content" :" Compose  a poem that explains the concept of recursion in programming "}
   ]
)
print(completion.choices[0].message)