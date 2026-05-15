# OCR Text Cleaning Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Clean up OCR results by removing weird symbols, normalizing ellipses, and collapsing spaces before they are sent to the translation service.

**Architecture:** Implement a private `_clean_text` method in `TranslationWorker` using regular expressions. This method will be called after a stable text is identified and before it's sent for translation.

**Tech Stack:** Python, `re` (Regex)

---

### Task 1: Setup and Failing Tests

**Files:**
- Create: `tests/test_text_cleaning.py`

**Step 1: Write the failing tests**

```python
import pytest
import re

# We will test the regex logic directly first, then as a method if possible
# Or mock TranslationWorker to test _clean_text

def clean_text_logic(text):
    if not text:
        return ""
    # Normalize long ellipses (4+ dots) to 3 dots
    text = re.sub(r'\.{4,}', '...', text)
    # Remove non-standard "garbage" characters
    # Keep letters, numbers, spaces, and common punctuation: .,!?;:'"-
    text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"-]', '', text)
    # Collapse multiple spaces and trim
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def test_normalize_ellipses():
    assert clean_text_logic("Wait for it....") == "Wait for it..."
    assert clean_text_logic("Wait for it..........") == "Wait for it..."

def test_remove_garbage():
    assert clean_text_logic("Hello #$@ World!") == "Hello World!"
    assert clean_text_logic("Price: 100€") == "Price 100" # € is removed as per regex

def test_collapse_spaces():
    assert clean_text_logic("  Too   many    spaces  ") == "Too many spaces"

def test_empty_input():
    assert clean_text_logic("") == ""
    assert clean_text_logic(None) == ""

def test_full_cleaning():
    input_text = "  Strange... symbols @#$% and    too many dots....  "
    expected = "Strange... symbols and too many dots..."
    assert clean_text_logic(input_text) == expected
```

**Step 2: Run test to verify it fails**

Since `clean_text_logic` is defined in the test for now to verify the logic, it might pass. But the goal is to verify this logic works before putting it into the worker.

Run: `pytest tests/test_text_cleaning.py`

**Step 3: Commit initial test**

```bash
git add tests/test_text_cleaning.py
git commit -m "test: add tests for OCR text cleaning logic"
```

---

### Task 2: Implement `_clean_text` in `TranslationWorker`

**Files:**
- Modify: `workers/translation_worker.py`

**Step 1: Add import and implement method**

Add `import re` at the top.
Add `_clean_text` to `TranslationWorker` class.

```python
    def _clean_text(self, text):
        if not text:
            return ""
        # Normalize long ellipses
        text = re.sub(r'\.{4,}', '...', text)
        # Remove non-standard "garbage" characters
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"-]', '', text)
        # Collapse multiple spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()
        return text
```

**Step 2: Update `tests/test_text_cleaning.py` to test the actual class method**

**Step 3: Run tests and verify PASS**

**Step 4: Commit implementation**

```bash
git add workers/translation_worker.py
git commit -m "feat: implement _clean_text in TranslationWorker"
```

---

### Task 3: Integrate `_clean_text` into `run()` loop

**Files:**
- Modify: `workers/translation_worker.py`

**Step 1: Update `run()` loop**

Locate where `stable_text` is assigned and call `_clean_text`.

```python
                # Pick the longer one as the stable text
                stable_text = text1 if len(text1) >= len(text2) else text2
                
                # CLEAN TEXT
                stable_text = self._clean_text(stable_text)
                
                if not stable_text:
                    continue
```

**Step 2: Verify syntax**

Run: `python3 -m py_compile workers/translation_worker.py`

**Step 3: Run all tests (if any others exist)**

**Step 4: Commit integration**

```bash
git add workers/translation_worker.py
git commit -m "feat: integrate text cleaning into TranslationWorker loop"
```
