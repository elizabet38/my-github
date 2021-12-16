import argparse
from github import Github
from typing import Dict, List, Any

ACCESS_TOKEN = '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'
g = Github(ACCESS_TOKEN)


class UserOrRepo():
    def __init__(self, name):
        self.is_repo = '/' in name
        self.name = name

    def get_list(self):
        if self.is_repo:
            return get_contr_list_(self.name)
        else:
            return get_repo_list_(self.name)


def get_user_info(args: Any) -> Dict[str, Any]:
    login = args.login
    user = g.get_user(login)
    info = {
        'name': user.name,
        'biography': user.bio,
        'company': user.company,
        'starred repos': len(list(user.get_starred())),
    }
    return info


def get_repo_info(args: Any) -> Dict[str, Any]:
    name = args.name
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
    waiting_list = [UserOrRepo(args.name)]
    depth = args.depth
    users_list = []
    repos_list = []
    while depth > 0 and waiting_list:
        new_list = []
        for name in waiting_list:
            new_names = [i for i in name.get_list() if
                         i not in users_list and
                         i not in repos_list and
                         i not in new_list]
            new_list.extend(new_names)
        if waiting_list[0].is_repo:
            repos_list.extend([i.name for i in waiting_list])
        else:
            users_list.extend([i.name for i in waiting_list])
        waiting_list = [UserOrRepo(i) for i in new_list]

        depth -= 1
    return users_list, repos_list


def dfs(args: Any) -> (List[str], List[str]):
    names = dfs_run(args.name, [], args.count)
    return [i for i in names if not UserOrRepo(i).is_repo],\
           [i for i in names if UserOrRepo(i).is_repo]


def dfs_run(name: str, names: List[str], count: int)\
        -> (List[str]):
    names.append(name)
    possible_names = [i for i in UserOrRepo(name).get_list()
                      if i not in names]
    while possible_names and len(names) < count:
        names = dfs_run(possible_names[0], names, count)
        possible_names = [i for i in UserOrRepo(name).get_list()
                          if i not in names]
    return names


def print_info(info: Dict[str, Any]) -> None:
    for key, value in info.items():
        print(f'{key}: {value}\n')


def print_list(list: List[str]) -> None:
    for num, item in enumerate(list):
        if num != len(list) - 1:
            print(f'{item}, ')
        else:
            print(f'{item}\n')


def print_two_lists(two_lists: (List[str], List[str])) -> None:
    users, repos = two_lists
    print('Users:\n')
    for user in users:
        print(f'{user}\n')
    print('Repos:\n')
    for repo in repos:
        print(f'{repo}\n')


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

    return parser


def my_github():
    parser = parser_init()
    args = parser.parse_args()
    output = args.func(args)
    args.out(output)