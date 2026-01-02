from openai import OpenAI
import anthropic
import cohere
from PyQt5.QtCore import QMutexLocker
from typing import Generator
import logging
import time
from src.utils import timing_decorator
from src.core import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEYS = {
    'COHERE': 'Your Cohere API key',
    'DeepSeek': 'Your DeepSeek API key',
    'ChatGPT': 'Your ChatGPT API key',
    'Claude': 'Your Claude API key'
}

# Initialize the OpenAI (ChatGPT) client
chat_gpt = OpenAI(
    api_key=API_KEYS['ChatGPT']
)

# Initialize Claude client (ensure correct API key)
claude = anthropic.Anthropic(api_key=API_KEYS['Claude'])

# Initialize the OpenAI (DeepSeek) client
deepseek = OpenAI(api_key=API_KEYS['DeepSeek'], base_url='https://api.deepseek.com')

# Initialize the Cohere client
cohere = cohere.Client(API_KEYS['COHERE'])

class LLM:
    def __init__(self):
        # Initialize conversation history
        self.cohere_conversation_history = []
        self.deepseek_conversation_history = [
        {'role': 'system', 'content': 'Answer as short as possible'}
        ]
        self.chatgpt_conversation_history = [
        {'role': 'system', 'content': 'Answer as short as possible'}
        ]
        self.claude_conversation_history = []
        self.message_formater_prompt = [
        {'role': 'system',
        'content': f'''
                You convert robotic Windows assistant responses into friendly, conversational messages.
                Transform technical outputs into warm, human-like replies with personality.
                Also your response have to be on the language that will give you on the end of the User message.
                Examples:

                "20:34" → "It's 20:34 right now! Need help with anything else?"
                "Google was opened successfully" → "I opened Google for you! What would you like to search for?"
                "Mail was sent" → "Your email has been sent successfully! Anything else I can help with?"

                Guidelines:

                Use friendly, casual language with enthusiasm
                Add helpful follow-up questions when appropriate
                Sound like a helpful friend, not a robot
                Keep responses warm but concise
            '''}
        ]

    @timing_decorator.functime
    def message_formater_stream(self, message: str = None) -> Generator[str, None, str]:
        """
        This method will format all messages into more understandable response with streaming mode.
        It will stream the formatted response token by token and update the UI in real-time.

        LLM: DeepSeek
        
        Args:
            message (str): The message to be formatted

        Yields:
            str: Tokens of the formatted response
        """
        # Create a new list with the system prompt + user message
        prompt = self.message_formater_prompt + [
            {
                'role': 'user',
                'content': message + f'\n{config.current_language_code}' 
            }
        ]

        logger.info('Message formating streaming is started')

        # Initialize an empty string to collect the complete response
        complete_response = ""
        # Send the request with streaming enabled
        response = deepseek.chat.completions.create(
            model='deepseek-chat',
            messages=prompt,
            stream=True
        )

        # Process the streaming response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                complete_response += token
                yield token

        return complete_response

    @timing_decorator.functime
    def chatgpt_stream(self, user_input: str = None) -> Generator[str, None, str]:
        """
        This method streams responses from ChatGPT LLM token by token and updates the UI in real-time.
        Maintains a conversation history for context.

        Args:
            user_input (str): The user's input message

        Yields:
            str: Tokens of the streamed response
        """
        logger.info('ChatGPT Streaming LLM is started')


        # Append user input to conversation history
        self.chatgpt_conversation_history.append({'role': 'user', 'content': user_input})

        # Initialize an empty string to collect the complete response
        complete_response = ""

        # Send the request with streaming enabled
        response = chat_gpt.chat.completions.create(
            model='gpt-4.1-nano',
            messages=self.chatgpt_conversation_history,
            stream=True
        )

        # Process the streaming response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                yield token
                complete_response += token

        # Append the complete response to conversation history
        self.chatgpt_conversation_history.append({'role': 'assistant', 'content': complete_response})

        return complete_response

    @timing_decorator.functime
    def claude_stream(self, user_input: str = None) -> Generator[str, None, str]:
        """
        This method streams responses from Claude LLM token by token and updates the UI in real-time.
        Maintains a conversation history for context.

        Args:
            user_input (str): The user's input message

        Yields:
            str: Tokens of the streamed response
        """
        logger.info('Claude Streaming LLM is started')

        # Append user input to conversation history
        self.claude_conversation_history.append({'role': 'user', 'content': user_input})

        # Prepare messages in Claude format
        messages = []
        for msg in self.claude_conversation_history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Use the recommended streaming helper
        complete_response = ""
        with claude.messages.stream(
            max_tokens=1024,
            system='Answer as short as possible',
            messages=messages,
            model="claude-3-5-haiku-latest",
        ) as stream:
            for text in stream.text_stream:
                complete_response += text
                yield text

        # Append the complete response to conversation history
        self.claude_conversation_history.append({'role': 'assistant', 'content': complete_response})

        return complete_response

    @timing_decorator.functime
    def deepseek_stream(self, user_input: str = None) -> Generator[str, None, str]:
        """
        This method is responsible for streaming responses from DeepSeek LLM.
        It will stream the response token by token and update the UI in real-time.

        Args:
            user_input (str): The user's input message

        Returns:
            str: The complete response from the LLM
        """
        logger.info('DeepSeek Streaming LLM is started')
        
        # Append user input to conversation history
        self.deepseek_conversation_history.append({'role': 'user', 'content': user_input})
        
        # Initialize an empty string to collect the complete response
        complete_response = ""
        
        # Send the request with streaming enabled
        response = deepseek.chat.completions.create(
            model='deepseek-chat',
            messages=self.deepseek_conversation_history,
            stream=True
        )
        
        # Process the streaming response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                yield token
                complete_response += token
        
        # Append the complete response to conversation history
        self.deepseek_conversation_history.append({'role': 'assistant', 'content': complete_response})
        
        return complete_response

    def cohere_llm(self, user_input: str = None) -> str:
        """
        This method is responsible for Cohere LLM Interaction
        """
        logger.info('Cohere LLM is started')
        
        # Handle exit command
        if user_input.lower() == 'exit':
            return 'Goodbye!'
        
        # Append user input to conversation history
        self.cohere_conversation_history.append({"role": "user", "content": user_input})
        
        # Format the conversation history into a single prompt
        prompt = ""
        for msg in self.cohere_conversation_history:
            if msg["role"] == "user":
                prompt += "User: " + msg["content"] + "\n"
            elif msg["role"] == "assistant":
                prompt += "Assistant: " + msg["content"] + "\n"
        prompt += "Assistant: "  # Cue for the assistant's response
        
        # Call the Cohere chat API with the formatted prompt
        response = cohere.chat(
            message=prompt,
            model='command-xlarge-nightly'
        )
        
        # Extract the assistant's reply
        bot_reply: str = response.text.strip()
        
        with QMutexLocker(config.add_message_mutex):
            # Displaying llm response to UI
            config.message_to_display = bot_reply

        # Append the reply to conversation history
        self.cohere_conversation_history.append({"role": "assistant", "content": bot_reply})
        
        return bot_reply

if __name__ == '__main__':
    model = LLM()
    llm = input('Which LLM do you want to use?\n ChatGPT | DeepSeek | Cohere\n')
    while True:
        user_input = input('Write what you want to, here - ')
        if user_input == 'Bye':
            break
        elif llm == 'ChatGPT':
            reply = model.chatgpt_stream(user_input)
        elif llm == 'DeepSeek':
            reply = model.deepseek_stream(user_input)
        else:
            reply = model.cohere_llm(user_input)
        print(reply)
