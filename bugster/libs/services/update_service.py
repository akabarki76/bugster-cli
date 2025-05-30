from abc import ABC, abstractmethod

from bugster.libs.mixins import DeleteMixin, SuggestMixin, UpdateMixin
from bugster.libs.services.test_cases_service import TestCasesService
from bugster.libs.utils.enums import GitCommand
from bugster.libs.utils.git import parse_diff_status, run_git_command
from bugster.libs.utils.nextjs.pages_finder import (
    generate_and_save_import_tree,
)


class UpdateService(ABC):
    """Base class for update services."""

    def __init__(self):
        self.mapped_changes = {}

    def _get_mapped_changes(self) -> dict:
        """Get the mapped changes of the user's repository."""
        diff_status = run_git_command(cmd_key=GitCommand.DIFF_STATUS)
        return parse_diff_status(diff_status=diff_status)

    def _get_import_tree(self) -> dict:
        """Get the import tree of the user's repository."""
        return generate_and_save_import_tree()

    def _setup(self):
        """Setup the update service."""
        self.import_tree = self._get_import_tree()
        self.mapped_changes = self._get_mapped_changes()

    @abstractmethod
    def run(self):
        """Run the update service."""
        pass


class SuggestOnlyService(UpdateService, SuggestMixin):
    def run(self):
        """Run the suggest only service."""
        self._setup()
        self.suggest()


class DeleteOnlyService(UpdateService, DeleteMixin):
    def run(self):
        """Run the delete only service."""
        self._setup()
        self.delete()


class UpdateOnlyService(UpdateService, UpdateMixin):
    def __init__(self):
        self.test_cases_service = TestCasesService()

    def run(self):
        """Run the update only service."""
        self._setup()
        self.update()


class DefaultUpdateService(UpdateService, UpdateMixin, SuggestMixin, DeleteMixin):
    def __init__(self):
        self.test_cases_service = TestCasesService()

    def run(self):
        """Run the default update service."""
        self._setup()
        self.update()
        self.suggest()
        self.delete()
