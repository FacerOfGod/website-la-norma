import os
import frontmatter
import deepl

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
CHANGED_FILES = os.getenv("CHANGED_FILES", "").splitlines()

SOURCE_LANG = "EN"
TARGET_LANG = "FR"
TARGET_SUFFIX = TARGET_LANG.lower()
SOURCE_DIR = "content/english"
TARGET_DIR = f"content/{TARGET_SUFFIX}"
EXCLUDED_FIELDS = {"images", "gallery", "logo"}
SEPARATOR = "|||DEEPL_SEPARATOR|||"

translator = deepl.Translator(DEEPL_API_KEY)

def collect_strings(value):
    strings = []
    if isinstance(value, str):
        if value.strip():
            strings.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            if k not in EXCLUDED_FIELDS:
                strings.extend(collect_strings(v))
    elif isinstance(value, list):
        for item in value:
            strings.extend(collect_strings(item))
    return strings

def apply_translations(value, translations):
    if isinstance(value, str):
        if value.strip():
            return translations.pop(0)
        return value
    elif isinstance(value, dict):
        return {k: (v if k in EXCLUDED_FIELDS else apply_translations(v, translations)) for k, v in value.items()}
    elif isinstance(value, list):
        return [apply_translations(item, translations) for item in value]
    else:
        return value

for file in CHANGED_FILES:
    if not file.startswith(SOURCE_DIR) or not file.endswith(".md"):
        continue

    src_path = file
    rel_path = os.path.relpath(src_path, SOURCE_DIR)
    translated_path = os.path.join(TARGET_DIR, rel_path)

    post = frontmatter.load(src_path)
    print(f"🔁 Translating: {src_path}")

    strings_to_translate = [post.content] + collect_strings(post.metadata)

    if strings_to_translate:
        # Join strings with a unique separator
        combined_text = SEPARATOR.join(strings_to_translate)
        translated_combined = translator.translate_text(combined_text, source_lang=SOURCE_LANG, target_lang=TARGET_LANG).text
        translated_texts = translated_combined.split(SEPARATOR)

        # First string is content
        translated_content = translated_texts.pop(0)
        translated_metadata = apply_translations(post.metadata, translated_texts)
    else:
        translated_content = post.content
        translated_metadata = post.metadata

    new_post = frontmatter.Post(translated_content, **translated_metadata)

    os.makedirs(os.path.dirname(translated_path), exist_ok=True)
    with open(translated_path, "wb") as f:
        frontmatter.dump(new_post, f)

    print(f"✅ Saved: {translated_path}")
