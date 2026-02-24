from git import Repo

repo = Repo("../")

def push_changes():
    new_files = repo.untracked_files
    modified = [d.a_path for d in repo.index.diff(None)]
    for n in new_files:
        print(f"adding new file {n}")
    repo.index.add(new_files)
    for m in modified:
        print(f"adding updated file {m}")
        repo.git.add(m)
    msg = f"{len(new_files)} new files & {len(modified)} modified files added"
    repo.index.commit(msg)

