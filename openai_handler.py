import signal
import time

import openai
from openai.types.chat import ChatCompletion


def handler(signum, frame):
    # swallow signum and frame
    raise Exception("end of time")


def make_auto_request(client: openai.Client, *args, **kwargs) -> ChatCompletion:
    ret = None
    while ret is None:
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(100)
            ret = client.chat.completions.create(*args, **kwargs)
            signal.alarm(0)
        except openai.RateLimitError:
            print("Rate limit exceeded. Waiting...")
            signal.alarm(0)
            time.sleep(5)
        except openai.APIConnectionError:
            print("API connection error. Waiting...")
            signal.alarm(0)
            time.sleep(5)
        except openai.APIError as e:
            print("Unknown API error")
            print(e)
            signal.alarm(0)
        except Exception as e:
            print("Unknown error. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(1)
    return ret

def openai_wrapper(message: str,
                   system_msg: str = "You are a helpful assistant good at math, coding, chess and logic.",
                   model: str = "gpt-4-turbo-preview", 
                   max_tokens: int = 2048, 
                   temperature: float = 0.9 ):
    if model.startswith("o1"):
        from openai import OpenAI
        client = OpenAI()
        API_MAX_RETRY = 3
        API_RETRY_SLEEP = 5
        
        for _ in range(API_MAX_RETRY):
            try:
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": message}
                ]
                messages = messages[1:]
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    n=1,
                )
                output = response.choices[0].message.content
                break
            except Exception as e:
                print(type(e), e)
                time.sleep(API_RETRY_SLEEP)
        
        return output
    else:
        client = openai.Client()
        output = make_auto_request(
                client=client,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": message}
                ]
        )
        return output

def openai_generate(prompts: list, **kwargs):
    outputs = []
    for prompt in prompts:
        output = openai_wrapper(prompt, **kwargs)
        if isinstance(output, str):
            outputs.append(output)
        else:
            outputs.append(output.choices[0].message.content)
    return outputs
        
    




if __name__ == "__main__":
    print(openai_generate(["Find the modulus of 100! with prime number 307. return the result in [] braces."],
    model="gpt-4o"))