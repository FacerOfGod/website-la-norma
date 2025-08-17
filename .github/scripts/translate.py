import os
import frontmatter
import deepl

# DeepL API configuration
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")  # GitHub Actions secret

# Translation settings
SOURCE_LANG = "EN"
TARGET_LANG = "FR"  # Uppercase codes required by DeepL
TARGET_SUFFIX = TARGET_LANG.lower()
SOURCE_DIR = "content/english"
TARGET_DIR = f"content/{TARGET_SUFFIX}"
EXCLUDED_FIELDS = {"images", "gallery", "logo"}

# Initialize DeepL Translator
translator = deepl.Translator(DEEPL_API_KEY)

def translate_text(text, target_lang, source_lang=None):
    """Translate text using DeepL Python library."""
    if not text.strip():
        return text  # skip empty text
    result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    return result.text

for root, _, files in os.walk(SOURCE_DIR):
    for file in files:
        if file.endswith(".md") and not file.endswith(f".{TARGET_SUFFIX}.md"):
            src_path = os.path.join(root, file)

            # Skip already translated folders
            if os.path.commonpath([src_path, os.path.join(SOURCE_DIR, TARGET_LANG)]) == os.path.join(SOURCE_DIR, TARGET_LANG):
                continue

            rel_path = os.path.relpath(src_path, SOURCE_DIR)  # e.g., 'activities/foo.md'
            translated_path = os.path.join(TARGET_DIR, rel_path)

            post = frontmatter.load(src_path)
            print(f"🔁 Translating: {src_path}")

            # Translate main content
            translated_content = translate_text(post.content, TARGET_LANG, SOURCE_LANG)

            # Translate metadata (except excluded fields)
            translated_metadata = {}
            for key, value in post.metadata.items():
                if key in EXCLUDED_FIELDS:
                    translated_metadata[key] = value
                elif isinstance(value, str):
                    translated_metadata[key] = translate_text(value, TARGET_LANG, SOURCE_LANG)
                else:
                    translated_metadata[key] = value

            new_post = frontmatter.Post(translated_content, **translated_metadata)

            # Ensure target directory exists
            os.makedirs(os.path.dirname(translated_path), exist_ok=True)

            # Save translated Markdown
            with open(translated_path, "wb") as f:
                frontmatter.dump(new_post, f)

            print(f"✅ Saved: {translated_path}")
