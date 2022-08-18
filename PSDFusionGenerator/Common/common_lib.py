import json
import re


def output_json(file_path: str, content: dict):
    # TODO エラーハンドリング
    with open(file_path, "w", encoding="utf-8_sig") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


def format_name(text: str):
    # 文字化け対応
    text = text.encode("utf-16", "surrogatepass").decode("utf-16")

    # フォルダ作成時の禁止用語コンバート
    text = re.sub(r'[\\/:*?"<>| ]+', "_", text)
    text = text.replace("\x00", "")
    if text == "":
        text = "_"
    return text