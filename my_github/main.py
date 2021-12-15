import argparse
from github import Github
from typing import Dict, List, Any
import sys

ACCESS_TOKEN = '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'
g = Github(ACCESS_TOKEN)


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
    name = args.name
    depth = args.depth
    users_list = []
    repos_list = []
    waiting_list = [name]
    is_repo = '/' in name
    while len(waiting_list) > 0 and depth >= 0:
        if is_repo:
            another_names_list = repos_list
            names_list = users_list
            get_list = get_contr_list_
        else:
            another_names_list = users_list
            names_list = repos_list
            get_list = get_repo_list_
        names = []
        for name in waiting_list:
            another_names_list.append(name)
            new_names = [i for i in get_list(name)
                         if i not in names_list and i not in names]
            names.extend(new_names)
        waiting_list = names

        depth -= 1
        is_repo = not is_repo
    return users_list, repos_list


def dfs(args: Any) -> (List[str], List[str]):
    return dfs_run(args.name, [], [], args.count)


def dfs_run(name: str, users: List[str], repos: List[str], count: int)\
        -> (List[str], List[str]):
    is_repo = '/' in name
    if is_repo:
        get_list = get_contr_list_
        check_list = users
        add_list = repos
    else:
        get_list = get_repo_list_
        check_list = repos
        add_list = users
    add_list.append(name)
    possible_names = [i for i in get_list(name) if i not in check_list]

    while len(users) + len(repos) < int(count) and possible_names:
        users, repos = dfs_run(possible_names[0], users, repos, count)
        if is_repo:
            get_list = get_contr_list_
            check_list = users
            add_list = repos
        else:
            get_list = get_repo_list_
            check_list = repos
            add_list = users
        possible_names = [i for i in get_list(name) if i not in check_list]
    return users, repos


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
        help='Number of steps of dfs'
    )
    _dfs.set_defaults(func=dfs, out=print_two_lists)

    return parser


def my_github():
    parser = parser_init()
    args = parser.parse_args()
    output = args.func(args)
    args.out(output)