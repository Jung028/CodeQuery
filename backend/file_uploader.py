import git

def clone_repository(github_url: str, destination: str):
    """ Clone the GitHub repository to a local directory """
    try:
        repo = git.Repo.clone_from(github_url, destination)
        print(f"Repository cloned to {destination}")
        return repo
    except Exception as e:
        print(f"Error cloning repo: {e}")
        return None
