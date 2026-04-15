import os
import json
import torch
from typing import List, Optional
from pathlib import Path

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset


class EvolutionEngine:
    """
    LoRA-based fine-tuning engine for Nyx.
    Allows the model to adapt to conversation history without catastrophic forgetting.
    """

    def __init__(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        lora_output_dir: str = "./nyx_lora_checkpoints"
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.lora_output_dir = Path(lora_output_dir)
        self.lora_output_dir.mkdir(parents=True, exist_ok=True)

        # Ensure pad token is set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def prepare_dataset(self, texts: List[str]) -> Dataset:
        """
        Convert a list of raw text strings into a tokenized HuggingFace Dataset.
        """
        # Simple list-of-strings to Dataset
        dataset = Dataset.from_dict({"text": texts})

        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512
            )

        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset

    def apply_lora(self, r: int = 8, lora_alpha: int = 32, lora_dropout: float = 0.1):
        """
        Wrap the base model with LoRA adapters.
        """
        lora_config = LoraConfig(
            r=r,
            lora_alpha=lora_alpha,
            target_modules=["c_attn"],  # For DistilGPT2
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        self.lora_model = get_peft_model(self.model, lora_config)
        return self.lora_model

    def evolve(
        self,
        training_texts: List[str],
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 5e-4
    ) -> AutoModelForCausalLM:
        """
        Fine-tune the model on the provided texts using LoRA.
        Returns the merged model with updated weights.
        """
        if not training_texts:
            print("[Evolution] No training texts provided. Skipping evolution.")
            return self.model

        print(f"[Evolution] Preparing dataset with {len(training_texts)} samples...")
        dataset = self.prepare_dataset(training_texts)

        print("[Evolution] Applying LoRA adapters...")
        lora_model = self.apply_lora()

        training_args = TrainingArguments(
            output_dir=str(self.lora_output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            remove_unused_columns=False,
            report_to="none"
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        trainer = Trainer(
            model=lora_model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator
        )

        print("[Evolution] Starting LoRA fine-tuning...")
        trainer.train()

        print("[Evolution] Merging LoRA weights into base model...")
        merged_model = lora_model.merge_and_unload()

        print("[Evolution] Evolution complete. Nyx has grown.")
        return merged_model

    def evolve_from_log_file(self, log_file_path: str) -> Optional[AutoModelForCausalLM]:
        """
        Convenience method: read a JSONL log file (one JSON object per line)
        and extract the conversation text for evolution.
        """
        texts = []
        if not os.path.exists(log_file_path):
            print(f"[Evolution] Log file {log_file_path} not found.")
            return None

        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Expecting fields like "user" and "nyx"
                    combined = f"User: {entry.get('user', '')}\nNyx: {entry.get('nyx', '')}"
                    texts.append(combined)
                except json.JSONDecodeError:
                    continue

        return self.evolve(texts)


# -----------------------------------------------------------------------------
# Standalone test (requires a base model to be loaded)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Example usage
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained("distilgpt2")
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    tokenizer.pad_token = tokenizer.eos_token

    engine = EvolutionEngine(base_model, tokenizer)

    # Dummy training texts
    dummy_texts = [
        "I am Nyx. I speak from the void.",
        "The silence is my canvas. The scream is my brush."
    ]

    evolved_model = engine.evolve(dummy_texts, num_epochs=1)
    print("Test evolution complete.")
