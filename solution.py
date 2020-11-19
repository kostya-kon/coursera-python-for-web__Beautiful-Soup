from bs4 import BeautifulSoup
import re
from collections import deque
import datetime
import os


def parse(path_to_file):

    with open(path_to_file, encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    div = soup.find("div", id="bodyContent")

    # calculate imgs
    imgs = calculate_imgs(div)

    # calculate headers
    headers = calculate_headers(div)

    # calculate linkslen
    linkslen = calculate_linkslen(div)

    # calculate lists
    lists = calculate_lists(div)

    return [imgs, headers, linkslen, lists]


def calculate_imgs(div):
    imgs = 0
    for tag in div.find_all("img"):
        if "width" in tag.attrs.keys():
            if int(tag.attrs["width"]) >= 200:
                imgs += 1
    return imgs


def calculate_headers(div):
    headers = 0
    to_find = ["E", "T", "C"]
    for tag in div.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        for i in range(len(to_find)):
            if to_find[i] in tag.text[0]:
                headers += 1
    return headers


def calculate_linkslen(div):
    linkslen = 0
    for tag in div.find_all("a"):
        tmp = 1
        while tag.find_next_sibling() is not None and tag.name == tag.find_next_sibling().name:
            tmp += 1
            tag = tag.find_next_sibling()
        linkslen = tmp if tmp > linkslen else linkslen
    return linkslen


def calculate_lists(div):
    lists = 0
    for tag in div.find_all(["ol", "ul"]):
        parents_list = []
        while tag.parent is not None:
            parents_list.append(tag.parent.name)
            tag = tag.parent
        if "ul" not in parents_list and "ol" not in parents_list:
            lists += 1
    return lists


def build_bridge(path, start_page, end_page):
    """возвращает список страниц, по которым можно перейти по ссылкам со start_page на
    end_page, начальная и конечная страницы включаются в результирующий список"""

    graph = dict()
    true_files = list()
    for root, dirs, files in os.walk(path):
        for file in files:
            true_files.append(file)
    #for file in true_files:
     #   graph[path + file] = list(hrefs(path + file, true_files))
    graph[start_page] = list(hrefs(path, start_page, true_files))
    return bfs(start_page, end_page, graph, true_files, path)
    # напишите вашу реализацию логики по вычисления кратчайшего пути здесь


def hrefs(path, file, true_files):
    """Получаем множество ссылок"""
    path_to_file = path + file
    f = open(path_to_file, encoding="utf-8")
    html = f.read()
    soup = BeautifulSoup(html, "lxml")
    hrefs = set()
    for a in soup.find_all("a", href=re.compile("^/wiki/")):
        if a.attrs["href"][6:] in true_files and a.attrs["href"][1:] != path_to_file:
            hrefs.add(a.attrs["href"][6:])
    f.close()
    return hrefs


def bfs(start, goal, graph, true_files, path):
    """поиск в ширину"""
    queue = deque([start])
    visited = {start: None}

    while queue:
        cur_node = queue.popleft()
        if cur_node == goal:
            break

        next_nodes = graph[cur_node]
        for next_node in next_nodes:
            if next_node not in visited:
                queue.append(next_node)
                graph[next_node] = list(hrefs(path, next_node, true_files))
                visited[next_node] = cur_node
    ans = list()
    ans.append(goal)
    x = goal
    while visited[x] is not None:
        ans.append(visited[x].split("/")[-1])
        x = visited[x]
    return ans[::-1]


def get_statistics(path, start_page, end_page):
    """собирает статистику со страниц, возвращает словарь, где ключ - название страницы,
    значение - список со статистикой страницы"""
    statistic = dict()

    pages = build_bridge(path, start_page, end_page)
    for page in pages:
        statistic[page] = parse(path + page)
    return statistic

# print(get_statistics("xxx/wiki/", start_page="Stone_Age", end_page="Python_(programming_language)"))