# coding:utf-8
from json import dump, dumps, load, loads
from subprocess import check_output
from os import path, remove
from sys import platform, argv
from hashlib import md5
import requests

class Repos(object):
    """ A class to get, save, update and clone all repositories from user """
    def __init__(self, username):
        self.username = username
        self.url = "https://api.github.com/users/%s/repos" % (self.username)
        self.check_repos()

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
                self.show_repos()
                return 1
            else:
                print 'not updated'.center(80)
                print 'updating...'.center(80)
                print 'updated'.center(80)
                print ' comparing '.center(80, '#')
                self.save_repos()
                self.check_repos()
                return 0

    def show_repos(self):
        """ Show a list of repositories """
        if path.exists('repos.json') and path.isfile('repos.json'):
            with open('repos.json') as f:
                repos = load(f)
                print ''
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
        pass

Repos(argv[1])
