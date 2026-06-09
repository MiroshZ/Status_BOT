from openai import AsyncOpenAI, OpenAIError


class AiServiceError(RuntimeError):
    """Raised when the AI provider cannot return a usable answer."""


class PolzaAiClient:
    def __init__(self, *, api_key: str, base_url: str, model: str, system_prompt: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._system_prompt = system_prompt

    async def ask(self, user_message: str) -> str:
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=900,
            )
        except OpenAIError as exc:
            raise AiServiceError("Polza.ai request failed") from exc

        message = completion.choices[0].message.content if completion.choices else None
        if not message:
            raise AiServiceError("Polza.ai returned an empty response")

        return message.strip()
