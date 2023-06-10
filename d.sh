#!/bin/bash --posix


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD=$(tput bold)
NORMAL=$(tput sgr0)


REQUIRED_CMDS=("wget" "apt-get" "pip")

for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}错误：$cmd 命令不存在。请安装它后再运行这个脚本。${NC}"
        exit 1
    fi
done


check_python_version() {
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")

    if [[ $PYTHON_VERSION != "3.9"* ]]; then
        echo -e "${RED}错误：Python 3.9 未安装或未设置为默认 Python 版本。请先安装 Python 3.9 并设置为默认版本后再运行这个脚本。${NC}"
        exit 1
    fi
}


detect_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        SYSTEM=$ID
    elif type lsb_release >/dev/null 2>&1; then
        SYSTEM=$(lsb_release -si)
    else
        echo -e "${RED}错误：无法检测到系统类型。请手动安装依赖并运行脚本。${NC}"
        exit 1
    fi
}


install_environment_centos() {
    echo -e "${YELLOW}${BOLD}安装环境 - CentOS${NORMAL}${NC}"
    yum -y update
    yum install -y google-chrome-stable
    yum install -y unzip screen git

    CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | awk -F. '{print $1}')
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

    echo -e "${GREEN}环境安装完成。${NC}\n"

}


install_environment_debian() {
    echo -e "${YELLOW}${BOLD}安装环境 - Debian/Ubuntu${NORMAL}${NC}"
    apt-get -y update
    apt-get install -y google-chrome-stable
    apt-get install -yqq unzip screen git


    CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | awk -F. '{print $1}')
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

    echo -e "${GREEN}环境安装完成。${NC}\n"

}


install_environment() {
    detect_system

    case $SYSTEM in
        "centos")
            install_environment_centos;;
        "debian" | "ubuntu")
            install_environment_debian;;
        *)
            echo -e "${RED}错误：不支持的系统类型。请手动安装依赖并运行脚本。${NC}"
            exit 1;;
    esac
}





configure_account() {
    echo -e "${YELLOW}${BOLD}配置账号信息${NORMAL}${NC}"
    read -p "请输入 Telegram Bot Token: " telegram_bot_token
    read -p "请输入 Telegram Chat ID: " telegram_chat_id
    read -p "请输入网站(带https://): " website
    read -p "请输入用户名: " username
    read -sp "请输入密码: " password
    echo


    echo -e "[Credentials]\ntelegram_bot_token = $telegram_bot_token\ntelegram_chat_id = $telegram_chat_id\nwebsite = $website\nusername = $username\npassword = $password" > config.ini


    mv config.ini exidian/config.ini

    echo -e "${GREEN}账号配置完成。${NC}\n"
}


run_program() {
    echo -e "${YELLOW}${BOLD}运行程序${NORMAL}${NC}"


    if screen -list | grep -q "ehueledu"; then
        echo -e "${RED}错误：程序已在运行中。请先结束程序。${NC}"
        return
    fi


    screen -dmS exidian


    screen -S exidian -p 0 -X stuff $'cd ehueledu\n'
    screen -S exidian -p 0 -X stuff $'ehueledu\n'


    sleep 1


    screen -S exidian -p 1 -X stuff $'python3 app.py\n'

    echo -e "${GREEN}程序已启动。您可以查看 screen 会话以查看日志。${NC}\n"


    while true; do
        echo -e "${YELLOW}${BOLD}程序状态菜单：${NORMAL}${NC}"
        echo -e "1. ${CYAN}进入 screen 窗口${NC}"
        echo -e "2. ${CYAN}返回主菜单${NC}"

        read -p "请输入您的选择（1-2）: " subchoice
        echo

        case $subchoice in
            1) screen -r exidian;;
            2) break;;
            *) echo -e "${RED}无效的选择。${NC}";;
        esac
    done
}


stop_program() {
    echo -e "${YELLOW}${BOLD}结束程序${NORMAL}${NC}"

    screen -S exidian -X quit

    echo -e "${GREEN}程序已结束。${NC}\n"
}


check_program_status() {
    echo -e "${YELLOW}${BOLD}检查程序状态${NORMAL}${NC}"

    if screen -list | grep -q "ehueledu"; then
        echo -e "${GREEN}程序正在运行。${NC}"
        echo


        while true; do
            echo -e "${YELLOW}${BOLD}程序状态菜单：${NORMAL}${NC}"
            echo -e "1. ${CYAN}进入 screen 窗口${NC}"
            echo -e "2. ${CYAN}返回主菜单${NC}"

            read -p "请输入您的选择（1-2）: " subchoice
            echo

            case $subchoice in
                1) screen -r exidian;;
                2) break;;
                *) echo -e "${RED}无效的选择。${NC}";;
            esac
        done
    else
        echo -e "${RED}程序未运行。${NC}"
        echo
    fi
}

# 菜单
while true; do
    echo -e "${YELLOW}${BOLD}菜单：${NORMAL}${NC}"
    echo -e "1. ${CYAN}安装环境${NC}"
    echo -e "2. ${CYAN}配置账号信息${NC}"
    echo -e "3. ${CYAN}运行程序${NC}"
    echo -e "4. ${CYAN}结束程序${NC}"
    echo -e "5. ${CYAN}检查程序状态${NC}"
    echo -e "6. ${CYAN}退出${NC}"

    read -p "请输入您的选择（1-7）: " choice
    echo

    case $choice in
        1) check_python_version && install_environment;;
        2) configure_account;;
        3) run_program;;
        4) stop_program;;
        5) check_program_status;;
        6) echo -e "${GREEN}退出。${NC}"; exit 0;;
        *) echo -e "${RED}无效的选择。${NC}";;
    esac
done