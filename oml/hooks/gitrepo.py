import os

from git import Repo, RemoteProgress, InvalidGitRepositoryError, GitCommandError
from oml.settings import load_model_metadata, GIT_REPOSITORY_URL


class GitRepositoryHook:

    def __init__(self):
        self.remote_url = GIT_REPOSITORY_URL

    def push_model(self, path):
        """Checkout branch with model name, commit and push to remote."""
        try:
            self._load_repo(path)
            if self.repo.active_branch.name != self.name:
                if self.name in self.repo.branches:
                    # If branch already exists, checkout
                    self.repo.git.checkout(self.name)
                else:
                    # If branch does not exist, checkout new branch from master
                    self.repo.git.checkout('master')
                    self.repo.git.checkout('-b', self.name)
            # Commit changes and push to remote
            self._commit_all()
            info = self.repo.remotes.origin.push(refspec='{}:{}'.format(self.name, self.name), progress=Progress())
            print(info[0].summary)
        except GitCommandError as e:
            print('Error: {}, {}'.format(e.stdout, e.stderr))

    def pull_model(self):
        """Clone repo if current directory is empty or pull latest changes from remote."""
        try:
            path = os.getcwd()
            if not os.listdir(path):
                print('Cloning repo at {}'.format(path))
                self.repo = Repo.clone_from(self.remote_url, path)
                print('Repo successfully loaded')
            else:
                print('Please call from empty folder')
                # , or clean and call from project folder to get latest changes.
        except Exception as e:
            print(e)

    def _commit_all(self, message='Automatic OML commit'):
        if self._has_uncommited_changes():
            self.repo.git.add('--all')
            self.repo.git.commit('-m', message)  # add more details like author

    def _load_repo(self, path, name=None):
        try:
            if name:
                self.name = name
            else:
                metadata = load_model_metadata(path)
                self.name = metadata['name']

            self.repo = Repo(path, search_parent_directories=True)
        except Exception as e:
            print(e)

    def _is_git_repo(self, path):
        try:
            Repo(path, search_parent_directories=True)
            return True
        except InvalidGitRepositoryError:
            return False

    def _has_uncommited_changes(self):
        return self.repo.is_dirty() or len(self.repo.untracked_files) > 0


class Progress(RemoteProgress):
    def line_dropped(self, line):
        print(line)

    def update(self, *args):
        print(self._cur_line)
