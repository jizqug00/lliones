# Import necessary libraries for model training and dataset preparation
from unsloth import FastLanguageModel

# For dataset
from datasets import load_dataset
from unsloth.chat_templates import get_chat_template

# For training
from trl import SFTTrainer, SFTConfig
from unsloth import is_bfloat16_supported

# Define model configuration parameters
max_seq_length = 4096  # Choose any! We auto support RoPE Scaling internally!
dtype = None  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.

# Define the repository and model name for loading the pre-trained model
repo_name = "unsloth"  # Repository containing the model
model_name = "Qwen2.5-0.5B"
# Load the pre-trained language model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=f"{repo_name}/{model_name}",  # Construct the full model path
    max_seq_length=max_seq_length,  # Set the maximum sequence length for tokenization
    dtype=dtype,  # Define the data type (e.g., float16, bfloat16) or auto-detect
    load_in_4bit=load_in_4bit  # Enable 4-bit quantization to reduce memory usage
)

# Apply LoRA (Low-Rank Adaptation) to the model for efficient fine-tuning.
# LoRA reduces the number of trainable parameters, making fine-tuning
# more memory-efficient while preserving model performance.
model = FastLanguageModel.get_peft_model(
    model,

    # LoRA rank: Determines the number of learnable parameters per layer.
    # Higher values increase expressiveness but also memory usage.
    r=128,  # Common values: 8, 16, 32, 64, 128

    # List of model layers to which LoRA will be applied.
    # These layers are typically key components in transformer-based models.
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],

    # Scaling factor for LoRA. It influences the learning rate adaptation.
    lora_alpha=256,

    # Dropout rate for LoRA layers. Setting it to 0 is optimized for stability.
    lora_dropout=0.1,  # A non-zero value can improve generalization in some cases.

    # Whether to train bias parameters. "none" is optimized for efficiency.
    bias="none",

    # Enable gradient checkpointing to reduce memory usage for long context models.
    # "unsloth" is a specialized version optimized for Unsloth models.
    use_gradient_checkpointing="unsloth",

    # Whether to use Rank-Stabilized LoRA (rslora), which adapts LoRA dynamically.
    use_rslora=False,

    # Configuration for LoftQ (Low-rank Quantization), which reduces model size.
    # Setting it to None disables LoftQ.
    loftq_config=None,
)

# Prepare dataset by formatting prompts for training
tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

def formatting_prompts_func(examples):
    prompt = examples["input"]
    output = examples["output"]

    messages = []
    for p, o in zip(prompt, output):
        el = [
              # {"role": "system", "content": "Eres un asistente experto en Leonés"},
              {"role": "user", "content": p},
              {"role": "assistant", "content": o},
            ]
        messages.append(el)

    texts = [tokenizer.apply_chat_template(ele, tokenize=False, add_generation_prompt = False).strip() + tokenizer.eos_token for ele in messages]
    return {"text": texts, }


dataset = load_dataset("unileon-robotics/lliones-dict-tr", split="train")
dataset_p = dataset.map(formatting_prompts_func, batched=True)

dataset_p[0]["text"]

# Configure the training process using SFTTrainer (Supervised Fine-Tuning Trainer)
trainer = SFTTrainer(
    model=model,  # The model to be fine-tuned
    tokenizer=tokenizer,  # Tokenizer used for text processing

    # Datasets for training and evaluation
    train_dataset=dataset_p,  # Training dataset

    # Training arguments
    args=SFTConfig(
        dataset_text_field="text",  # Field name containing text data in the dataset
        max_seq_length=max_seq_length,  # Maximum sequence length for input text

        dataset_num_proc=4,  # Number of CPU processes for dataset preprocessing
        packing=False,  # Whether to concatenate multiple examples into a single sequence

        # Training batch size per GPU/TPU/CPU
        per_device_train_batch_size=8,

        # Number of steps to accumulate gradients before performing a backward pass
        gradient_accumulation_steps=1,

        # Number of training epochs
        num_train_epochs=3,
        # Number of steps
        # max_steps=200,

        # Number of warmup steps for the learning rate scheduler
        warmup_ratio=0.1,

        # Learning rate for the optimizer
        learning_rate=2e-4,

        # Use 16-bit floating-point precision (FP16) if BFloat16 is not supported
        fp16=True,
        bf16=False,  # Use BFloat16 if the hardware supports it

        # Frequency of logging training progress
        logging_steps=500,

        # Optimizer type; "adamw_8bit" reduces memory usage
        optim="paged_adamw_8bit",

        # Weight decay for regularization (helps prevent overfitting)
        weight_decay=0.01,

        # Type of learning rate scheduler (linear decay in this case)
        lr_scheduler_type="linear",

        # Directory to save training outputs (e.g., checkpoints, logs)
        output_dir=None,

        save_strategy="no",

        # Disable reporting to external loggers (e.g., WandB, TensorBoard)
        report_to="none",
    ),
)

# Start the fine-tuning process
trainer_stats = trainer.train(resume_from_checkpoint = False)

# Save the quantized fine-tuned model for later use
model.save_pretrained_gguf(f"/home/student/ws/models/{model_name}/outputs/gguf/{model_name}", tokenizer, quantization_method = "q5_k_m")

model = FastLanguageModel.for_training(model) # Enable native 2x faster inference

# Save the LoRA model for later use
model.save_pretrained_merged(f"/home/student/ws/models/{model_name}/outputs/loras/{model_name}", tokenizer, save_method="lora")

