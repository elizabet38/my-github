import argparse
from typing import Dict, List, Any
from github import Github
from dataclasses import dataclass

with open('TOKEN.txt') as f:
    ACCESS_TOKEN = f.read().splitlines()[0]
g = Github(ACCESS_TOKEN)


@dataclass
class BaseClass:
    name: str

    def neighbours(self):
        raise NotImplementedError('Not implemented')


class User(BaseClass):
    def __init__(self, name):
        super().__init__(name)

    def neighbours(self):
        return get_repo_list_(self.name)


class Repo(BaseClass):
    def __init__(self, name):
        super().__init__(name)

    def neighbours(self):
        return get_contr_list_(self.name)


def get_user_or_repo(name):
    if '/' in name:
        return Repo(name)
    return User(name)


def get_user_info(args: Any) -> Dict[str, Any]:
    return get_user_info_(args.login)


def get_user_info_(login: str) -> Dict[str, Any]:
    user = g.get_user(login)
    info = {
        'name': user.name,
        'biography': user.bio,
        'url': user.url,
        'company': user.company,
        'starred repos': len(list(user.get_starred())),
    }
    return info


def get_repo_info(args: Any) -> Dict[str, Any]:
    return get_repo_info_(args.name)


def get_repo_info_(name: str) -> Dict[str, Any]:
    repo = g.get_repo(name)
    info = {
        'name': repo.full_name,
        'description': repo.description,
        'forks count': repo.forks_count,
        'stargazers count': repo.stargazers_count,
        'main language': repo.language,
        'languages': list(repo.get_languages()),
        'parent': repo.parent.full_name if repo.parent is not None else None
    }
    return info


def get_repo_list(args: Any) -> List[str]:
    return get_repo_list_(args.login)


def get_repo_list_(user_login: str) -> List[str]:
    user = g.get_user(user_login)
    return [i.full_name for i in user.get_repos()]


def get_contr_list(args: Any) -> List[str]:
    return get_contr_list_(args.name)


def get_contr_list_(repo_name: str) -> List[str]:
    repo = g.get_repo(repo_name)
    return [i.login for i in repo.get_contributors()]


def bfs(args: Any) -> (List[str], List[str]):
    waiting_list = [get_user_or_repo(args.name)]
    depth = args.depth
    users_list = []
    repos_list = []
    while depth > 1 and waiting_list:
        new_list = []
        for name in waiting_list:
            new_names = [i for i in name.neighbours() if
                         i not in users_list and
                         i not in repos_list and
                         i not in new_list]
            new_list.extend(new_names)
        if isinstance(waiting_list[0], Repo):
            repos_list.extend([i.name for i in waiting_list])
        else:
            users_list.extend([i.name for i in waiting_list])
        waiting_list = [get_user_or_repo(i) for i in new_list]

        depth -= 1
    if isinstance(waiting_list[0], Repo):
        repos_list.extend([i.name for i in waiting_list])
    else:
        users_list.extend([i.name for i in waiting_list])

    return users_list, repos_list


def dfs(args: Any) -> (List[str], List[str]):
    names = dfs_run(args.name, [], args.count)
    return [i for i in names if isinstance(get_user_or_repo(i), User)], \
           [i for i in names if isinstance(get_user_or_repo(i), Repo)]


def dfs_run(name: str, names: List[str], count: int) \
        -> (List[str]):
    names.append(name)
    possible_names = [i for i in get_user_or_repo(name).neighbours()
                      if i not in names]
    while possible_names and len(names) < count:
        names = dfs_run(possible_names[0], names, count)
        possible_names = [i for i in get_user_or_repo(name).neighbours()
                          if i not in names]
    return names


def find_repos(args: Any) -> List[Dict[str, Any]]:
    repos_list = g.search_repositories(args.text)[:args.num]
    return [get_repo_info_(i.full_name) for i in repos_list]


def print_info(info: Dict[str, Any]) -> None:
    for key, value in info.items():
        print(f'{key}: {value}')


def print_list(list: List[str]) -> None:
    for num, item in enumerate(list):
        print(f'{item}')


def print_two_lists(two_lists: (List[str], List[str])) -> None:
    users, repos = two_lists
    print('Users:')
    for user in users:
        print(f'{user}')
    print('Repos:')
    for repo in repos:
        print(f'{repo}')


def print_list_with_info(list: List[Dict[str, Any]]):
    for n, i in enumerate(list):
        print(f'{n}.')
        print_info(i)
        print('\n')


def parser_init() -> argparse.ArgumentParser:
    """Parser initialization."""
    parser = argparse.ArgumentParser(usage='my-github <command> [parameter]')

    subparsers = parser.add_subparsers(
        dest='action',
        metavar='<command>',
        required=True
    )

    _get_user_info = subparsers.add_parser(
        'get_user_info',
        help='Get information about user'
    )
    _get_user_info.add_argument(
        'login',
        help="User's login"
    )
    _get_user_info.set_defaults(func=get_user_info, out=print_info)
    _get_repo_info = subparsers.add_parser(
        'get_repo_info',
        help='Get information about repository'
    )
    _get_repo_info.add_argument(
        'name',
        help="Full name of repository"
    )
    _get_repo_info.set_defaults(func=get_repo_info, out=print_info)
    _get_repo_list = subparsers.add_parser(
        'get_repo_list',
        help='Get list of repositories, owned by user'
    )
    _get_repo_list.add_argument(
        'login',
        help="User's login"
    )
    _get_repo_list.set_defaults(func=get_repo_list, out=print_list)
    _get_contr_list = subparsers.add_parser(
        'get_contr_list',
        help='Get list of contributors of project'
    )
    _get_contr_list.add_argument(
        'name',
        help="Full name of repository"
    )
    _get_contr_list.set_defaults(func=get_contr_list, out=print_list)
    _bfs = subparsers.add_parser(
        'bfs',
        help='Start bfs from user or repo'
    )
    _bfs.add_argument(
        'name',
        help='Name of user or repo'
    )
    _bfs.add_argument(
        '--depth',
        default=3,
        required=False,
        type=int,
        help='Depth of bfs'
    )
    _bfs.set_defaults(func=bfs, out=print_two_lists)
    _dfs = subparsers.add_parser(
        'dfs',
        help='Start dfs from user or repo'
    )
    _dfs.add_argument(
        'name',
        help='Name of user or repo'
    )
    _dfs.add_argument(
        '--count',
        default=100,
        required=False,
        type=int,
        help='Number of steps of dfs'
    )
    _dfs.set_defaults(func=dfs, out=print_two_lists)
    _find_repos = subparsers.add_parser(
        'find_repos',
        help='Find repositories with text in name'
    )
    _find_repos.add_argument(
        'text',
        help='Text to find'
    )
    _find_repos.add_argument(
        '--num',
        default=10,
        required=False,
        type=int,
        help='Number of repositories to show'
    )
    _find_repos.set_defaults(func=find_repos, out=print_list_with_info)

    return parser


def my_github():
    parser = parser_init()
    args = parser.parse_args()
    output = args.func(args)
    args.out(output)
