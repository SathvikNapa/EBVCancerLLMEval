import logging
import re

from mcqa.application.evaluation import QAEvaluation
from mcqa.domain.patterns import Patterns
from mcqa.domain.postprocessor import PostProcessorInterface
from mcqa.domain.response_generator import ResponseGeneratorResponse, ResponseMetadata

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


class PostProcessor(PostProcessorInterface):
    """Post-processor for extracting information from responses using regex patterns."""

    def __init__(self, model: str):
        """Initializes the PostProcessor with the specified model.

        Args:
            model (str): The model used for response generation.
        """
        self.model = model
        self.evaluation = QAEvaluation()

    def _extract_regex(self, pattern: str, text: str, default_value: str = "") -> str:
        """Extracts text matching a regex pattern.

        Args:
            pattern (str): The regex pattern to search for.
            text (str): The text to search within.
            default_value (str, optional): The value to return if no match is found. Defaults to "".

        Returns:
            str: The extracted text or the default value if no match is found.
        """
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1) if match else default_value

    def _find_regex(self, pattern, text: str) -> list:
        """Finds all occurrences of a regex pattern in the text.

        Args:
            pattern (Pattern): The regex pattern to search for.
            text (str): The text to search within.

        Returns:
            list: A list of all matches found.
        """
        return pattern.findall(text)

    def postprocess(self, generated_response: str, actual_answer: str) -> ResponseGeneratorResponse:
        """Post-processes the response to extract relevant fields and evaluate the answer.

        Args:
            generated_response (str): The response text to be processed.
            actual_answer (str): The actual answer to compare against.

        Returns:
            ResponseGeneratorResponse: The post-processed response containing extracted fields.
        """
        logger.debug("Response: %s", generated_response)
        generated_answer = self._extract_regex(Patterns.answer, generated_response, "Answer")
        excerpts = self._extract_regex(Patterns.excerpts, generated_response, "RelevantExcerpts")
        thinking = self._extract_regex(Patterns.thinking, generated_response, "Thinking")
        foundational_knowledge = self._extract_regex(
            Patterns.foundational_knowledge, generated_response, "FoundationalKnowledge"
        )
        evaluation = self.evaluation.evaluate(generated_answer, actual_answer)

        logger.debug("Evaluation: %s", evaluation)

        return ResponseGeneratorResponse(
            generated_answer=generated_answer,
            actual_answer=actual_answer,
            evaluation=evaluation,
            excerpts=excerpts,
            thinking=thinking,
            foundational_knowledge=foundational_knowledge,
            metadata=ResponseMetadata(model=self.model)
        )

    def postprocess_rephrase(self, generated_response: str) -> list:
        """Post-processes the response to extract rephrased questions, options, and answers.

        Args:
            generated_response (str): The response text to be processed.

        Returns:
            list: A list of tuples containing questions, options, and answers.
        """
        logger.debug("Response: %s", generated_response)
        generated_questions = self._find_regex(Patterns.question_pattern, generated_response)
        generated_options = self._find_regex(Patterns.options_pattern, generated_response)
        generated_answers = self._find_regex(Patterns.answer_pattern, generated_response)

        return list(zip(generated_questions, generated_options, generated_answers))

    def postprocess_synthetic(self, generated_response: str) -> list:
        """Post-processes the response to extract synthetic questions, options, and answers.

        Args:
            generated_response (str): The response text to be processed.

        Returns:
            list: A list of tuples containing questions, options, and answers.
        """
        logger.debug("Response: %s", generated_response)
        generated_questions = self._find_regex(Patterns.question_pattern, generated_response)
        generated_options = self._find_regex(Patterns.options_pattern, generated_response)
        generated_answers = self._find_regex(Patterns.answer_pattern, generated_response)

        return list(zip(generated_questions, generated_options, generated_answers))