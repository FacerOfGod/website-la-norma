import os
import frontmatter
import deepl

# DeepL API configuration
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# Translation settings
SOURCE_LANG = "EN"
TARGET_LANG = "FR"
TARGET_SUFFIX = TARGET_LANG.lower()
SOURCE_DIR = "content/english"
TARGET_DIR = f"content/{TARGET_SUFFIX}"
EXCLUDED_FIELDS = {"images", "gallery", "logo"}

# Initialize DeepL Translator
translator = deepl.Translator(DEEPL_API_KEY)

def translate_text(text, target_lang, source_lang=None):
    """Translate a string using DeepL."""
    if not text.strip():
        return text
    result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    return result.text

def translate_metadata(value):
    """Recursively translate metadata, skipping excluded fields."""
    if isinstance(value, str):
        return translate_text(value, TARGET_LANG, SOURCE_LANG)
    elif isinstance(value, dict):
        return {k: (v if k in EXCLUDED_FIELDS else translate_metadata(v)) for k, v in value.items()}
    elif isinstance(value, list):
        return [translate_metadata(item) for item in value]
    else:
        return value

for root, _, files in os.walk(SOURCE_DIR):
    for file in files:
        if file.endswith(".md") and not file.endswith(f".{TARGET_SUFFIX}.md"):
            src_path = os.path.join(root, file)

            # Skip already translated folders
            if os.path.commonpath([src_path, os.path.join(SOURCE_DIR, TARGET_LANG)]) == os.path.join(SOURCE_DIR, TARGET_LANG):
                continue

            rel_path = os.path.relpath(src_path, SOURCE_DIR)
            translated_path = os.path.join(TARGET_DIR, rel_path)

            post = frontmatter.load(src_path)
            print(f"🔁 Translating: {src_path}")

            # Translate main content
            translated_content = translate_text(post.content, TARGET_LANG, SOURCE_LANG)

            # Translate metadata recursively
            translated_metadata = translate_metadata(post.metadata)

            new_post = frontmatter.Post(translated_content, **translated_metadata)

            os.makedirs(os.path.dirname(translated_path), exist_ok=True)

            with open(translated_path, "wb") as f:
                frontmatter.dump(new_post, f)

            print(f"✅ Saved: {translated_path}")
