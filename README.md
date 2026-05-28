# MT Exercise 4: Byte Pair Encoding, Beam Search

This repository is a starting point for the 4th and final exercise. As before, fork this repo to your own account and then clone it into your preferred directory.

---

## Requirements

- Python 3.10 must be installed. The command `python3` (or `python` on Windows) should be available from your terminal or command prompt.
- `virtualenv` must be installed. Install it with:

  ```powershell
  pip install virtualenv

macOS/Linux users: No special setup needed; shell scripts should run normally.

Windows users: Either use Windows Subsystem for Linux (WSL) or a Unix-compatible shell like Git powershell.
If you're using PowerShell or Command Prompt, manual setup is required.

### Setup Instructions

## For macOS / Linux / WSL / Git powershell users

Clone your fork of the repository + Create a virtual environment:
   ```
   git clone https://github.com/[your-username]/mt-exercise-4
   cd mt-exercise-4 

   ```
    ./scripts/make_virtualenv.sh

Important: Then activate the env by executing the source command that is output by the shell script above.

Install required dependencies - Follow the instructions provided in the exercise PDF.

Download data:

       python ./scripts/download_huggingface_data.py --src en --trg nl --out data

You can choose any supported direction except `de-en`. Good options are `en-nl`, `en-it`, `en-ro`, `nl-en`, `it-en`, or `ro-en`.


Train the model:

       ./scripts/train.sh

*the training process can be interrupted at any time. The best checkpoint will always be saved automatically.

Evaluate the model:

       ./scripts/evaluate.sh

## For Windows (Command Prompt / PowerShell users)
Manually create and activate a virtual environment:

        python -m venv mt_env
        mt_env/Scripts/activate

Note: The make_virtualenv.sh script will not work in native Windows shells.

Manually download the dataset

Use the Python downloader script directly, for example:

       python scripts/download_huggingface_data.py --src en --trg nl --out data

If you want a different language pair, replace `--src` and `--trg` with one of the supported directions listed above.

Modify, train, and evaluate
Once setup is complete, use the instructions in the exercise PDF to run training and evaluation (either by adapting the .sh scripts manually, or by using Git powershell/WSL).

#### Notes for Windows Users

  Using Git powershell or WSL is highly recommended for compatibility.

  If using native PowerShell or Command Prompt:

  Manual recreation of shell script steps will be necessary.

  Always activate your virtual environment before running any training or evaluation steps. 


# BPE Preprocessing and Configuration Modification Notes

## 1. Byte Pair Encoding Experiments

This experiment compares the impact of different vocabulary construction methods on neural machine translation quality. The translation direction selected for this experiment is English -> Dutch, namely en-nl. All experiments use the same translation direction so that the differences between the word-level model and the BPE-based models can be compared more easily.

According to the assignment requirements, I conducted three experiments:

A word-level model without BPE, with the vocabulary size limited to 2000
A BPE-based model with a BPE vocabulary size of 2000
A BPE-based model with a BPE vocabulary size of 5000

Both the BPE 2000 and BPE 5000 settings use joint BPE, which means that English and Dutch share the same set of BPE codes. In addition, vocabulary filtering is applied during the apply-bpe stage, so that the BPE output contains, as much as possible, only subword units that appear in the corresponding language-specific training vocabulary with sufficient frequency.

## 1.1 Data Preparation

First, I downloaded the English-Dutch parallel corpus from the IWSLT 2017 dataset:

```powershell
python scripts/download_huggingface_data.py --src en --trg nl
```

After downloading, the `data` folder contains the following files:

```text
train.en
train.nl
dev.en
dev.nl
test.en
test.nl
```

To reduce training time, I randomly sampled 100k parallel sentence pairs from the training set. This step was organized into the script `sample_train.py`. It can be run as follows:

```powershell
python sample_train.py --sample-size 100000
```

The script uses the same randomly selected line indices to sample sentences from `train.en` and `train.nl`, ensuring that the parallel sentence pairs remain aligned. The sampled files are saved as:

```text
train_new.en
train_new.nl
```

## 1.2 Joint BPE and Vocabulary Filtering

Before running BPE preprocessing, I first ran `sample_train.py` to generate `train_new.en` and `train_new.nl`.

For easier reproduction, all BPE preprocessing steps were organized into the script `preprocess_bpe.py`. To generate the BPE-related files, the script can be run directly from the project root directory:

```powershell
python preprocess_bpe.py
```

This script automatically performs the following steps:

Merge `train_new.en` and `train_new.nl` into `train.all`
Learn BPE 2000 and BPE 5000 codes
Generate vocabulary filter files for English and Dutch separately
Apply BPE 2000 and BPE 5000 with vocabulary filtering to the train, dev, and test sets
Generate the shared BPE vocabulary files used by JoeyNMT:
`vocab.bpe_2000` and `vocab.bpe_5000`

The main commands are still listed below to explain the preprocessing procedure in detail.

## BPE 2000

First, learn the BPE 2000 codes:

```powershell
Get-Content data\train.all |
subword-nmt learn-bpe -s 2000 --total-symbols |
Set-Content -Encoding utf8 data\bpe_2000.codes
```

Then, generate the vocabulary filter files for English and Dutch separately. Here, the counts produced by `get-vocab` are kept because these files are used as the `--vocabulary` input for `apply-bpe`:

```powershell
Get-Content data\train_new.en |
subword-nmt apply-bpe -c data\bpe_2000.codes |
subword-nmt get-vocab |
Set-Content -Encoding utf8 data\vocab.bpe2000.en.with_counts
```

```powershell
Get-Content data\train_new.nl |
subword-nmt apply-bpe -c data\bpe_2000.codes |
subword-nmt get-vocab |
Set-Content -Encoding utf8 data\vocab.bpe2000.nl.with_counts
```

Next, vocabulary filtering is used when applying BPE 2000 to the train, dev, and test data. This follows the best practice described in the `subword-nmt` README: first learn joint BPE codes on the merged training data of the two languages, then create separate vocabulary filter files for each language, and finally use `--vocabulary` and `--vocabulary-threshold 50` when processing the train, dev, and test sets.

This approach keeps the benefit of shared joint BPE while restricting the BPE output to subwords that are frequent enough in the corresponding language, reducing noise caused by unreasonable or very low-frequency subword units.

```powershell
Get-Content data\train_new.en |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.en.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\train.bpe2000.en
```

```powershell
Get-Content data\train_new.nl |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.nl.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\train.bpe2000.nl
```

```powershell
Get-Content data\dev.en |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.en.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\dev.bpe2000.en
```

```powershell
Get-Content data\dev.nl |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.nl.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\dev.bpe2000.nl
```

```powershell
Get-Content data\test.en |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.en.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\test.bpe2000.en
```

```powershell
Get-Content data\test.nl |
subword-nmt apply-bpe -c data\bpe_2000.codes --vocabulary data\vocab.bpe2000.nl.with_counts --vocabulary-threshold 50 |
Set-Content -Encoding utf8 data\test.bpe2000.nl
```

Finally, create the shared BPE vocabulary file used by JoeyNMT. This file is different from the vocabulary filter files above. JoeyNMT’s `voc_file` only needs tokens and does not require counts:

```powershell
Get-Content data\train.bpe2000.en, data\train.bpe2000.nl |
subword-nmt get-vocab |
ForEach-Object { ($_ -split "\s+")[0] } |
Set-Content -Encoding utf8 data\vocab.bpe_2000
```

## BPE 5000

The preprocessing procedure for BPE 5000 is the same as that for BPE 2000. The only difference is that the BPE vocabulary size is changed from 2000 to 5000.


## 1.3 JoeyNMT Configuration Modifications

All three experiments use English -> Dutch, so the language settings are:

```yaml
src:
  lang: en
trg:
  lang: nl
```

The word-level baseline does not use BPE. Instead, it uses complete words as tokens. The configuration uses:

```yaml
train: data/train_new
dev: data/dev
test: data/test
level: "word"
```

For the word-level model, the vocabulary size is limited to 2000. During training, I used `voc_limit: 2000`, allowing JoeyNMT to build the source vocabulary and target vocabulary from the training data:

```yaml
src:
  voc_limit: 2000
trg:
  voc_limit: 2000
```

After training, JoeyNMT saves the vocabulary files in the `output_word` directory:

```text
output_word/src_vocab.txt
output_word/trg_vocab.txt
```

During testing, JoeyNMT test mode does not rebuild the vocabulary from the training set. Therefore, in the test configuration, I changed the setup to use the vocabulary files saved during training:

```yaml
src:
  voc_file: output_word/src_vocab.txt
trg:
  voc_file: output_word/trg_vocab.txt
```

These two vocabulary files are word-level vocabularies, not BPE vocabularies. Since the source and target sides use different word-level vocabularies, the following settings are used:

```yaml
tied_embeddings: False
tied_softmax: False
```

The output directory for the word-level baseline is:

```yaml
model_dir: output_word
```

For BPE 2000, the already preprocessed BPE files are used:

```yaml
train: data/train.bpe2000
dev: data/dev.bpe2000
test: data/test.bpe2000
voc_file: data/vocab.bpe_2000
```

For BPE 5000, the configuration uses:

```yaml
train: data/train.bpe5000
dev: data/dev.bpe5000
test: data/test.bpe5000
voc_file: data/vocab.bpe_5000
```

Although the BPE data has already been segmented into subwords, the configuration still uses:

```yaml
level: "word"
```

The reason is that BPE has already been applied to the data in advance, and the subword units are already separated by spaces. Therefore, JoeyNMT only needs to read these subwords as ordinary tokens.

Both BPE 2000 and BPE 5000 use a shared vocabulary file, so the following settings are used:

```yaml
tied_embeddings: True
tied_softmax: True
```

Their corresponding output directories are:

```yaml
model_dir: output_bpe2000
model_dir: output_bpe5000
```

## 1.4 Tokenizer and BLEU Settings

At first, I tried to use:

```yaml
tokenizer_type: "space"
```

However, the current version of JoeyNMT does not support this tokenizer type and reports the following error:

```text
space: Unknown tokenizer type
```

Therefore, I finally removed `tokenizer_type: "space"` and used `level: "word"` together with the default basic tokenizer to read the already space-separated BPE tokens.

To output BLEU scores, I added the following settings to the `testing` section:

```yaml
beam_size: 1
beam_alpha: 1.0
max_output_length: 100
eval_metrics: ["bleu"]
sacrebleu_cfg:
  tokenize: "13a"
  lowercase: false
```

All three models use the same beam size to ensure a fair comparison. The setting `lowercase: false` means that case-sensitive BLEU is calculated.

For BPE models, JoeyNMT directly outputs BPE-token BLEU. To obtain the final comparable BLEU score, I removed the `@@` markers from the output and then calculated BLEU against the original reference file `data/test.nl`.

## 1.5 Training and Testing Commands

After completing data preprocessing and modifying the configuration files, I trained three models separately:

- Word-level baseline
- BPE 2000
- BPE 5000

## Word-level Baseline

When training the word-level baseline, I used `voc_limit: 2000`:

```powershell
python -m joeynmt train .\configs\transformer_sample_config.yaml
```

When testing the word-level baseline, I used the vocabulary files saved after training:

```powershell
python -m joeynmt test .\configs\transformer_sample_config.yaml --output .\output_word\word_beam1.hyps.test
```

## BPE 2000

Train the BPE 2000 model:

```powershell
python -m joeynmt train .\configs\transformer_sample_config_bpe2000.yaml
```

Evaluate the BPE 2000 model on the test set and save the output to a specified file:

```powershell
python -m joeynmt test .\configs\transformer_sample_config_bpe2000.yaml --output .\output_bpe2000\bpe2000_beam1.hyps.test
```

Here, `--output` is used to specify the output filename. This makes it easier to save test outputs under different beam sizes later, and it also prevents different results from being overwritten or mixed together.

Since the output of the BPE 2000 model still contains the BPE marker `@@`, the `@@` markers need to be removed after testing. Then BLEU is recalculated using the original reference translation file `data/test.nl`.

The command is:

```powershell
python evaluate_detok_bleu.py .\output_bpe2000\bpe2000_beam1.hyps.test
```

## BPE 5000

The training and testing procedure for the BPE 5000 model is the same as that for the BPE 2000 model.

## 1.6 Scripts

I organized the main steps into reusable scripts so that the experiment can be reproduced more conveniently.

## 1.6.1 Training Data Sampling Script

The training data sampling script is:

```text
sample_train.py
```

This script is used to randomly sample a specified number of parallel sentence pairs from the full training set. It uses the same random line indices to extract English and Dutch sentences, ensuring that the parallel sentence pairs do not become misaligned.

The output files are:

```text
train_new.en
train_new.nl
```

Run the script as follows:

```powershell
python sample_train.py --sample-size 100000
```

## 1.6.2 BPE Preprocessing Script

The BPE preprocessing script is:

```text
preprocess_bpe.py
```

This script is used to generate all BPE-related files. It is equivalent to the manual BPE preprocessing commands listed in Section 1.2. It performs the following steps:

- Merge `train_new.en` and `train_new.nl` to generate the joint BPE training file `train.all`
- Learn BPE 2000 and BPE 5000 codes separately
- Generate vocabulary filter files with counts for English and Dutch separately
- Apply BPE to the train, dev, and test sets using `--vocabulary` and `--vocabulary-threshold 50`
- Create the shared BPE vocabulary used by JoeyNMT, removing the counts from the `get-vocab` output and keeping only the tokens

Run the script as follows:

```powershell
python preprocess_bpe.py
```

## 1.6.3 BLEU Evaluation Script

After testing the BPE models, the output still contains the BPE marker `@@`. Therefore, I wrote an additional BLEU post-processing script:

```text
evaluate_detok_bleu.py
```

This script takes a specified hypothesis file as input, removes the `@@` markers from the output, and recalculates the final BLEU score using the detokenized file and the original reference translation file `data/test.nl`.

For example, to calculate the final BLEU score of BPE 2000 with beam size 1:

```powershell
python evaluate_detok_bleu.py .\output_bpe2000\bpe2000_beam1.hyps.test
```

The script also generates a corresponding detokenized file in the same directory as the hypothesis file. For example, given the input file:

```text
output_bpe2000\bpe2000_beam1.hyps.test
```

the script generates:

```text
output_bpe2000\bpe2000_beam1.detok
```

## 1.6.4 Manual Translation Inspection Script

To manually inspect translation quality, I also wrote a script for viewing test output translations:

```text
show_translation.py
```

This script takes a specified hypothesis file as input, reads the source sentence, reference translation, and model hypothesis, and prints the first several examples in the format of `SRC`, `REF`, and `HYP`. This makes it easier to compare translation quality manually.

By default, the script outputs the first 50 examples. A different number of examples can also be specified using the second argument.

For example, to view and save the first 50 translation results of the word-level baseline:

```powershell
python show_translation.py .\output_word\word_beam1.hyps.test
```

The script automatically saves the results as a `.manual_check.txt` file.
