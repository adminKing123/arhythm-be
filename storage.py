from config import CONFIG
from github import Github

github_token = CONFIG["GITHUB_TOKEN"]
branch_name = CONFIG["GITHUB_BRANCH_NAME"]
github_repo_name = CONFIG["GITHUB_REPO_NAME"]
github = Github(github_token)
repo = github.get_user().get_repo(github_repo_name)


def upload_file(file_path, content, commit_message):
    try:
        repo.create_file(
            path=file_path,
            message=commit_message,
            content=content,
            branch=branch_name
        )

        return True
    except Exception as e:
        print(f"Failed to upload {file_path} to GitHub: {e}")
        return False
    
def delete_file(file_path, commit_message):
    try:
        contents = repo.get_contents(file_path, ref=branch_name)
        repo.delete_file(
            path=file_path,
            message=commit_message,
            sha=contents.sha,
            branch=branch_name
        )
        return True
    except Exception as e:
        print(f"Failed to delete {file_path} from GitHub: {e}")
        return False