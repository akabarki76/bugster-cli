from rich.console import Console
from rich.status import Status
from rich.text import Text

from bugster.libs.utils.files import get_specs_pages
from bugster.libs.utils.git import get_diff_changes_per_page
from bugster.libs.utils.nextjs.pages_finder import (
    get_affected_pages,
    is_nextjs_page,
)

console = Console()


class UpdateMixin:
    """Update mixin."""

    def update(self, *args, **kwargs):
        """Update existing specs."""
        modified_files = self.mapped_changes["modified"]
        console.print(f"✓ Found {len(modified_files)} modified files")
        affected_pages = get_affected_pages(
            diff_files=modified_files, import_tree=self.import_tree
        )
        diff_changes_per_page = get_diff_changes_per_page(import_tree=self.import_tree)
        updated_specs = 0
        specs_pages = get_specs_pages()

        for page in affected_pages:
            if page in specs_pages:
                spec = specs_pages[page]
                spec_data = spec["data"]
                spec_path = spec["path"]

                with Status(
                    f"[yellow]Updating: {spec_path}[/yellow]", spinner="dots"
                ) as status:
                    diff = "\n==========\n".join(diff_changes_per_page[page])
                    self.test_cases_service.update_spec_by_diff(
                        spec_data=spec_data, diff_changes=diff, spec_path=spec_path
                    )
                    status.stop()
                    console.print(f"✓ [green]{spec_path}[/green] updated")
                    updated_specs += 1
            else:
                text = Text("✗ Page ")
                text.append(page, style="red")
                text.append(" not found in test cases")
                console.print(text)

        if updated_specs > 0:
            console.print(
                f"✓ Updated {updated_specs} spec{'' if updated_specs == 1 else 's'}"
            )


class SuggestMixin:
    """Suggest mixin."""

    def suggest(self, *args, **kwargs):
        """Suggest new specs."""
        added_files = self.mapped_changes["new"]
        console.print(f"✓ Found {len(added_files)} added files")
        suggested_specs = []

        for file in added_files:
            if is_nextjs_page(file_path=file):
                pass

        if len(suggested_specs) > 0:
            for spec in suggested_specs:
                console.print(f"⚠️  Suggested new spec: {spec}")


class DeleteMixin:
    """Delete mixin."""

    def delete(self, *args, **kwargs):
        """Delete existing specs."""
        deleted_files = self.mapped_changes["deleted"]
        console.print(f"✓ Found {len(deleted_files)} deleted files")
        deleted_pages = set()

        for file in deleted_files:
            if is_nextjs_page(file_path=file):
                deleted_pages.add(file)

        specs_pages = get_specs_pages()
        deleted_specs = 0

        for page in deleted_pages:
            if page in specs_pages:
                spec = specs_pages[page]
                spec_path = spec["path"]

                with Status(
                    f"[yellow]Deleting: {spec_path}[/yellow]", spinner="dots"
                ) as status:
                    self.test_cases_service.delete_spec_by_spec_path(
                        spec_path=spec_path
                    )
                    status.stop()
                    console.print(f"✓ [green]{spec_path}[/green] deleted")
                    deleted_specs += 1

        if deleted_specs > 0:
            console.print(
                f"✓ Deleted {deleted_specs} spec{'' if deleted_specs == 1 else 's'}"
            )
