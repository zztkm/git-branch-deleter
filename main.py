import subprocess

from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        rows = generate_table_data()
        table.add_columns(*rows[0])
        table.add_rows(rows[1:])

    def key_j(self):
        """ Move cursor down. """
        table = self.query_one(DataTable)
        now = table.cursor_row
        table.move_cursor(row = now + 1)

    def key_k(self):
        """ Move cursor up. """
        table = self.query_one(DataTable)
        now = table.cursor_row
        table.move_cursor(row = now - 1)


def generate_table_data() -> list[tuple[str, str]]:
    branch_names = get_branch_names()
    # 先頭に空文字を追加する
    data = [("check", "branch")]
    for branch in branch_names:
        data.append(("", branch))
    return data


def get_branch_names() -> list[str]:
    """ Get branch names from the current git repository. """
    result = subprocess.run(
        ["git", "branch"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


app = TableApp()
if __name__ == "__main__":
    app.run()
