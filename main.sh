function git_install() {
    : INSTALL GIT :
    installed=$(which git)
    if [ $installed = "/usr/bin/git" ];then
        echo 'Installed'
    else
        sudo apt install -y git
        echo 'Installed'
    fi
}

function jq_install() {
    : INSTALL JQ :
    installed=$(which jq)
    if [ $installed = "/usr/bin/jq" ];then
        echo "Installed"
    else
        sudo apt install -y jq
        echo "Installed"
    fi
}

function check_username() {
    : DISPLAY USERNAME :
    user=$(echo $USERNAME)
    if [ -e "/home/$user/gitsync" ];then
        username=$(cat /home/$user/gitsync/user_data)
        echo $username
    else
        echo "None"
    fi
}

function git_configure() {
    : DEFINE NAME AND EMAIL IN GITHUB OR ONLY SHOW :
    name=$(git config --global user.name)
    email=$(git config --global user.email)
    name_s=$(echo $name | wc -c)
    if [ $name_s -lt 1 ];then
        echo "Type your name: "
        read name
        git config --global user.name "$name"
        echo "Type your email: "
        read email
        git config --global user.email $email
        git_configure
    else
        echo "$name, $email"
    fi
}

function define_username() {
    : GET CURRENT USER AND DEFINE USERNAME OF GITHUB :
    user=$(echo $USERNAME) # get current user
    echo "Type your username of github: "
    read username
    username_s=$(echo $username | wc -c)
    if [ $username_s -gt 1 ];then
        mkdir /home/$user/gitsync
        echo "$username" > /home/$user/gitsync/user_data # stores username on this file
        echo "Username defined"
    fi
}

function cloning() {
    : CLONING ALL REPOS :
    user=$(echo $USERNAME)
    echo "Clone all repos? (S/n): "
    read response
    response="${response^^}"
    if [ $response = 'S' ];then
        if [ ! -e 'repos/' ];then
            mkdir repos/
        fi
        cd repos/
        if [ ! -e "/home/$user/gitsync" ];then
            define_username
        fi
        username=$(cat /home/$user/gitsync/user_data)
        if [ -e "repos" ];then
            rm -r repos
            resp=$(wget https://api.github.com/users/$username/repos)
        else
            resp=$(wget https://api.github.com/users/$username/repos)
        fi
        n_repos=$(cat repos | jq '. | length')
        ((n_repos = n_repos - 1))
        for i in  `seq 0 1 $n_repos`; do
            name=$(cat repos | jq ".[$i].name")
            repo=$(cat repos | jq ".[$i].clone_url")
            repo=$(echo $repo | xargs)
            echo $name
            echo "[NOW] Cloning $name..."
            git clone $repo
        done
    else
        echo "Okay..."
    fi
}

function main() {
    : CALL ALL THE FUNCTIONS :
    echo 
    echo "Git stats ---~> $(git_install)"
    echo "Jq stats  ---~> $(jq_install)"
    echo "Username  ---~> $(check_username)"
    echo "Git infos ---~> $(git_configure)"
    echo ""
    cloning
}

main
