from github import Github
import config

def get_version(owner: str = 'Flint15', repo_name: str = 'EVA-2.0', file_path: str = "application_version.txt") -> str:
    """
    Fetch contents of a file in a private GitHub repo using PyGithub.
    Returns the file content as text.
    """
    # 1. Initialize PyGithub client
    gh = Github('')

    # 2. Get the repository object (will raise if not found or no permission)
    repo = gh.get_repo(f"{owner}/{repo_name}")

    # 3. Request the file contents. file_path must be repo-relative!
    contents = repo.get_contents(file_path)
    raw_bytes = contents.decoded_content  # this is already bytes

    version: str = raw_bytes.decode("utf-8").strip() # remove '\n' or whitespace

    return version

def check_version(current_version: str = config.application_version, latest_version: str = get_version()) -> str:
    if current_version != latest_version:
        return 'Not matches'

if __name__ == "__main__":
    try:
        # Note: file_path here is just the filename inside the repo, not the full URL.
        text = get_version()
        print(text)
    except Exception as e:
        print(f"Error: {e}")
