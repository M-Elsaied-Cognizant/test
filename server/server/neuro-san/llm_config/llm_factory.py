from typing import Any
from typing import Dict
from typing import List
import json
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from neuro_san.internals.run_context.langchain.langchain_llm_factory import LangChainLlmFactory


class LlmFactory(LangChainLlmFactory):
    """
    Factory class for LLM operations

    Most methods take a config dictionary which consists of the following keys:

        "model_name"                The name of the model.
                                    Default if not specified is "gpt-3.5-turbo"

        "temperature"               A float "temperature" value with which to
                                    initialize the chat model.  In general,
                                    higher temperatures yield more random results.
                                    Default if not specified is 0.7

        "prompt_token_fraction"     The fraction of total tokens (not necessarily words
                                    or letters) to use for a prompt. Each model_name
                                    has a documented number of max_tokens it can handle
                                    which is a total count of message + response tokens
                                    which goes into the calculation involved in
                                    get_max_prompt_tokens().
                                    By default the value is 0.5.

        "max_tokens"                The maximum number of tokens to use in
                                    get_max_prompt_tokens(). By default this comes from
                                    the model description in this class.
    """

    def create_base_chat_model(self, config: Dict[str, Any],
                               callbacks: List[BaseCallbackHandler] = None) -> BaseLanguageModel:
        """
        Create a BaseLanguageModel from the fully-specified llm config.
        :param config: The fully specified llm config which is a product of
                    _create_full_llm_config() above.
        :param callbacks: A list of BaseCallbackHandlers to add to the chat model.
        :return: A BaseLanguageModel (can be Chat or LLM)
                Can raise a ValueError if the config's class or model_name value is
                unknown to this method.
        """
        # Construct the LLM
        llm: BaseLanguageModel = None
        chat_class: str = config.get("class")
        if chat_class is not None:
            chat_class = chat_class.lower()

        model_name: str = config.get("model_name")
        # print("model_name",model_name)

        # print(f"In TestLlmFactory for {json.dumps(config, sort_keys=True, indent=4)}")
        if chat_class == "primary-gpt":
            # print("Creating azure-openai-msi")
            model_kwargs: Dict[str, Any] = {
                "stream_options": {
                    "include_usage": True
                }
            }
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            llm = AzureChatOpenAI(
                # For authenticating with MSI
                azure_ad_token_provider=token_provider,
                # For authenticating with key 
                #api_key = self.get_value_or_env(config, "openai_api_key",
                #                                                "OPENAI_API_KEY"),
                azure_endpoint = self.get_value_or_env(config, "azure_endpoint", "AZURE_OPENAI_ENDPOINT"),
                api_version = self.get_value_or_env(config,"openai_api_version","OPENAI_API_VERSION"),
                azure_deployment = self.get_value_or_env(config, "deployment_name", "AZURE_DEPLOYMENT_NAME"),
                # model_name=model_name,
                temperature=self.get_value_or_env(config, "temperature","TEMPERATURE"),
                openai_organization=self.get_value_or_env(config, "openai_organization",
                                                            "OPENAI_ORG_ID"),
                openai_proxy=self.get_value_or_env(config, "openai_organization",
                                                    "OPENAI_PROXY"),
                request_timeout=config.get("request_timeout"),
                max_retries=config.get("max_retries"),
                presence_penalty=config.get("presence_penalty"),
                frequency_penalty=config.get("frequency_penalty"),
                seed=self.get_value_or_env(config, "seed","SEED"),
                logprobs=config.get("logprobs"),
                top_logprobs=config.get("top_logprobs"),
                logit_bias=config.get("logit_bias"),
                streaming=True,     # streaming is always on. Without it token counting will not work.
                n=1,                # n is always 1.  neuro-san will only ever consider one chat completion.
                top_p=self.get_value_or_env(config, "top_p","TOP_P"),
                max_tokens=config.get("max_tokens"),    # This is always for output
                tiktoken_model_name=config.get("tiktoken_model_name"),
                stop=config.get("stop"),
                model_kwargs=model_kwargs,
                callbacks=callbacks,
                )
            # print("api_key:", self.get_value_or_env(config, "openai_api_key", "OPENAI_API_KEY"))
            # print("azure_endpoint:", self.get_value_or_env(config, "azure_endpoint", "AZURE_OPENAI_ENDPOINT"))
            # print("api_version:", config.get("openai_api_version"))
            # print("azure_deployment:", self.get_value_or_env(config, "deployment_name", "AZURE_DEPLOYMENT_NAME"))
            # print("temperature:", config.get("temperature"))
            # print("openai_organization:", self.get_value_or_env(config, "openai_organization", "OPENAI_ORG_ID"))
            # print("openai_proxy:", self.get_value_or_env(config, "openai_organization", "OPENAI_PROXY"))
            # print("request_timeout:", config.get("request_timeout"))
            # print("max_retries:", config.get("max_retries"))
            # print("presence_penalty:", config.get("presence_penalty"))
            # print("frequency_penalty:", config.get("frequency_penalty"))
            # print("seed:", config.get("seed"))
            # print("logprobs:", config.get("logprobs"))
            # print("top_logprobs:", config.get("top_logprobs"))
            # print("logit_bias:", config.get("logit_bias"))
            # print("streaming:", True)
            # print("n:", 1)
            # print("top_p:", config.get("top_p"))
            # print("max_tokens:", config.get("max_tokens"))
            # print("tiktoken_model_name:", config.get("tiktoken_model_name"))
            # print("stop:", config.get("stop"))
            # print("model_kwargs:", model_kwargs)
            # print("callbacks:", callbacks)
            
        elif chat_class == "fallback-gpt":
            # print("Creating azure-openai-msi")
            model_kwargs: Dict[str, Any] = {
                "stream_options": {
                    "include_usage": True
                }
            }
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            llm = AzureChatOpenAI(
                # For authenticating with MSI
                azure_ad_token_provider=token_provider,
                # For authenticating with key 
                # api_key = self.get_value_or_env(config, "fallback_openai_api_key",
                #                                                  "FALLBACK_OPENAI_API_KEY"),
                azure_endpoint = self.get_value_or_env(config, "fallback_azure_endpoint", "FALLBACK_OPENAI_ENDPOINT"),
                api_version = self.get_value_or_env(config,"openai_api_version","OPENAI_API_VERSION"),
                azure_deployment = self.get_value_or_env(config, "fallback_deployment_name", "FALLBACK_DEPLOYMENT_NAME"),
                # model_name=model_name,
                temperature=self.get_value_or_env(config, "temperature","TEMPERATURE"),
                openai_organization=self.get_value_or_env(config, "openai_organization",
                                                            "OPENAI_ORG_ID"),
                openai_proxy=self.get_value_or_env(config, "openai_organization",
                                                    "OPENAI_PROXY"),
                request_timeout=config.get("request_timeout"),
                max_retries=config.get("max_retries"),
                presence_penalty=config.get("presence_penalty"),
                frequency_penalty=config.get("frequency_penalty"),
                seed=self.get_value_or_env(config, "seed","SEED"),
                logprobs=config.get("logprobs"),
                top_logprobs=config.get("top_logprobs"),
                logit_bias=config.get("logit_bias"),
                streaming=True,     # streaming is always on. Without it token counting will not work.
                n=1,                # n is always 1.  neuro-san will only ever consider one chat completion.
                top_p=self.get_value_or_env(config, "top_p","TOP_P"),
                max_tokens=config.get("max_tokens"),    # This is always for output
                tiktoken_model_name=config.get("tiktoken_model_name"),
                stop=config.get("stop"),
                model_kwargs=model_kwargs,
                callbacks=callbacks,
                )
            
        # elif chat_class in ("slm-openai", "llama-openai"):
        #     model_kwargs: Dict[str, Any] = {
        #         "stream_options": {
        #             "include_usage": True
        #         }
        #     }
        #     llm = AzureAIChatCompletionsModel(
        #         credential=self.get_value_or_env(config, "openai_api_key", "OPENAI_API_KEY"),
        #         endpoint=self.get_value_or_env(config, "azure_endpoint", "OPENAI_API_BASE"),
        #         model_name=model_name,
        #         temperature=0,
        #         callbacks=callbacks,
        #         model_kwargs=model_kwargs,
        #         api_version=config.get("openai_api_version"),
        #         max_tokens=None,
        #         timeout=None,
        #         max_retries=2
        #     )
            
       
        elif chat_class is None:
            raise ValueError(f"Class name {chat_class} for model_name {model_name} is unspecified.")
        else:
            raise ValueError(f"Class {chat_class} for model_name {model_name} is unrecognized.")

        return llm