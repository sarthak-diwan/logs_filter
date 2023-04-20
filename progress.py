progress_data = {}

class Progress:
    def __init__(self, file_name) -> None:
        self.progress="starting..."
        self.file = file_name

    def update_progress(self, progress_str):
        self.progress = progress_str

    