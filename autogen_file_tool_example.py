import os
from autogen_core.tools import FunctionTool

def read_text_file(file_path: str) -> str:
    """
    Reads the text from a given file path.
    Returns the file contents or an error if the file does not exist.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

text_file_reader_tool = FunctionTool(
    func=read_text_file,
    name="text_file_reader_tool",
    description="Reads text from a file given a 'file_path' string."
)
