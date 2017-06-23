# coding:utf-8
from json import dump, dumps, load, loads
from subprocess import check_output
from os import path, remove, system
from sys import platform, argv
from hashlib import md5
import requests

class Repos(object):
    """ A class to get, save, update and clone all repositories from user """
    def __init__(self, username):
        self.username = username
        self.url = "https://api.github.com/users/%s/repos" % (self.username)
        self.check_repos()
        self.input_user()

    @staticmethod
    def generate_hash_file(filename):
        """ Generate a hash for one file and return this """
        hasher = md5()
        if path.exists(filename):
            with open(filename, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def compare_hash(filename, filenameX):
        """ Generate a hash for both files and compare them """
        hasher = md5()
        hashO, hashX = Repos.generate_hash_file(filename), Repos.generate_hash_file(filenameX)
        return 1 if hashO == hashX else 0

    def get(self):
        """ Get response from request github API """
        try:
            req = requests.get(self.url)
            return loads(req.text)
        except Exception as e:
            raise Exception(e)

    def save_repos(self, fn='repos.json'):
        """ Save the response (only important links) of self.get """
        repos = self.get()
        all_repos = []
        try:
            for idx, repo in enumerate(repos):
                name, url, url_clone = repo['name'], repo['url'], repo['clone_url']
                r = {'name' : name, 'links' : {'url' : url, 'url_clone' : url_clone}}
                all_repos.append(r)
                with open (fn, 'w') as f:
                    dump(all_repos, f, ensure_ascii=True)
        except TypeError:
            print "You exceed limits on API"

    def check_repos(self):
        """ Update the response """
        current = self.save_repos('current.json')
        if path.exists('repos.json') and path.isfile('repos.json'):
            print ' comparing '.center(80, '#')
            if Repos.compare_hash('repos.json', 'current.json'):
                remove('current.json')
                print 'is updated'.center(80)
                print ' comparing '.center(80, '#')
                return 1
            else:
                print 'not updated'.center(80)
                print 'updating...'.center(80)
                print 'updated'.center(80)
                print ' comparing '.center(80, '#')
                self.save_repos()
                self.check_repos()
                return 0
        else:
            self.save_repos()
            self.check_repos()

    def show_repos(self):
        """ Show a list of repositories """
        if path.exists('repos.json') and path.isfile('repos.json'):
            with open('repos.json') as f:
                repos = load(f)
                print ' repositories '.center(80, '-')
                for idx, repo in enumerate(repos):
                    print '[%d] - %s'.center(65) % (idx, repo['name'])
                print ''
                print ' repositories '.center(80, '-')

    def check_git(self):
        """ Check if git is installed """
        installed = check_output(['where', 'git']) if platform.startswith('win') else check_output(['which', 'git'])
        if not installed:
            raise Exception("Install 'git' to clone repositories :D")

    def clone_all(self):
        """ Clone all repositories """
        with open('repos.json') as f:
            repos = load(f)
            print " status ".center(80, '^')
            for repo in repos:
                print "Cloning: %s".center(80) % (repo['name'])
                system("git clone %s" % repo['links']['url_clone'])
            else:
                print "All repositories were cloned".center(80)
            print " status ".center(80, '^')
            self.input_user()
    
    @staticmethod
    def clone_url(idx):
        """ Clone only one repository """
        with open('repos.json') as f:
            repo = load(f)[idx]
            print " status ".center(80, '^')
            print "Cloning: %s".center(80) % (repo['name'])
            system("git clone %s" % repo['links']['url_clone'])
            print " status ".center(80, '^')
            self.input_user()

    def input_user(self):
        """ Get a input from user to manipulate the program """
        print ' user input '.center(80, '~')
        print '[1] - Clone all'.center(80)
        print '[2] - Clone specific (type number)'.center(80)
        print '[3] - Quit'.center(80)
        inp = int(input("".center(40)))
        print ' user input '.center(80, '~')
        if inp == 1:
            self.clone_all()
        elif inp == 2:
            self.show_repos()
            print ' user input '.center(80, '~')
            idx = int(input("Choose a repo: ".center(60)))
            print ' user input '.center(80, '~')
            Repos.clone_url(idx)
        else:
            print 'exiting...'.center(80)
            exit(0)

Repos(argv[1])
