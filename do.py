#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import os
import re
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('--build', '-b', action='store_true')
parser.add_argument('--create-network', '-n', action='store_true')
parser.add_argument('--run', '-r', action='store_true')
parser.add_argument('--attach', '-a', metavar='container_name')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    quiet=False,
    hide_args=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        if hide_args:
            args_to_show = args[:hide_args] + ('...',)
        else:
            args_to_show = args
        if any([re.search(r'\s', i) for i in args_to_show]):
            print()
            for i in args_to_show: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args_to_show):
                if i != len(args_to_show)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8')
            if out != 'exact': result = result.strip()
        return result

def git_state():
    diff = invoke('git diff', out=True)
    diff_cached = invoke('git diff --cached', out=True)
    with open('git-state.txt', 'w') as git_state:
        git_state.write(invoke('git show --name-only', out=True)+'\n')
        if diff:
            git_state.write('\n===== diff =====\n')
            git_state.write(diff+'\n')
        if diff_cached:
            git_state.write('\n===== diff --cached =====\n')
            git_state.write(diff_cached+'\n')

#===== main =====#
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.build:
    git_state()
    invoke('docker build -t dans-smtp:latest .')

if args.create_network:
    invoke('docker network create --driver bridge dans-smtp-net')

if args.run:
    invoke('docker rm -f dans-smtp')
    if os.path.exists('run_extra_args.txt'):
        with open('run_extra_args.txt') as f:
            extra_args = f.read().split()
    else:
        extra_args = []
    invoke(
        'docker', 'run',
        '-d',
        '--name', 'dans-smtp',
        '--log-opt', 'max-size=10m',
        '--log-opt', 'max-file=3',
        '-p', '8025:8025',
        '--restart', 'always',
        *extra_args,
        'dans-smtp:latest',
        hide_args=2,
    )
    invoke('docker network connect dans-smtp-net dans-smtp')

if args.attach:
    invoke(f'docker network connect dans-smtp-net {args.attach}')
