import numpy as np
from transformers import DataCollatorForLanguageModeling
from typing import List, Union, Any, Dict
from constants import SENTENCE_SEPARATOR


class DataCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    def torch_call(
        self, examples: List[Union[List[int], Any, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        batch = super().torch_call(examples)

        # The prompt ends with the response key plus a newline.  We encode this and then try to find it in the
        # sequence of tokens.  This should just be a single token.
        response_token_ids = self.tokenizer.encode(SENTENCE_SEPARATOR)

        labels = batch["labels"].clone()

        for i in range(len(examples)):
            response_token_ids_start_idx = None
            for idx in np.where(batch["labels"][i] == response_token_ids[0])[0]:
                response_token_ids_start_idx = idx
                break

            if response_token_ids_start_idx is None:
                raise RuntimeError(
                    f'Could not find response key {response_token_ids} in token IDs {batch["labels"][i]}'
                )

            response_token_ids_end_idx = response_token_ids_start_idx + 1

            # Make pytorch loss function ignore all tokens up through the end of the response key
            labels[i, :response_token_ids_end_idx] = -100

        batch["labels"] = labels

        return batch
