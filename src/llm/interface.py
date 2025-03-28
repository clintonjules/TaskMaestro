from .access import LLMAccess

class LLMInterface:
    """
    A generic interface for LLMs that wraps the LLMAccess layer.
    This class is responsible for constructing the prompt with a system message and user message,
    then calling the underlying LLM via the LLMAccess class.
    """

    def __init__(self, access_config, system_message=None):
        """
        Initialize the LLMInterface with a configuration for LLMAccess and an optional system message.

        :param access_config: Dictionary containing configuration for LLMAccess.
        :param system_message: Optional system message to include in every prompt (default: 'You are a helpful assistant.')
        """
        self.access = LLMAccess(access_config)
        self.system_message = system_message or "You are a helpful assistant."

    def prompt(self, user_prompt: str, **kwargs) -> str:
        """
        Build the message payload by including the system message and the user's prompt,
        then call the LLM via the access layer.

        :param user_prompt: The user provided prompt.
        :param kwargs: Additional parameters to pass to the LLMAccess call.
        :return: The response from the LLM as a string.
        """
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_prompt}
        ]
        # The first argument to call is a placeholder prompt; the messages are passed via kwargs.
        return self.access.call('', messages=messages, **kwargs)
