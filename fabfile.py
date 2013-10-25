from fabric.api import local, env, sudo

def prep():
    test()
    commit()

def test():
    local('py.test -sx --cov-report term-missing --cov .')

def commit():
    local('git pull')
    local('git add -p && git commit')
#def bootstrap():
    #require('root', 
