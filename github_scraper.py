from bs4 import BeautifulSoup
import requests
import re
import json

def find_login(page_content):

    type = find_type(page_content)

    if type == 'User':
        elements = page_content.find('title')
        pattern = r"^\S+"
        match = re.search(pattern, elements.text)

        if match:
            login = match.group()
            return login
    else: 

            elements = page_content.find("meta", property="profile:username")
            login = elements["content"]
            return(login)

def find_avatar_url(username):
    
    page = requests.get("https://github.com/search?q=" + username + "&type=users")
    payload = json.loads(page.text)["payload"]["results"][0]
    url = payload["avatar_url"]

    avatar_url = re.sub(r'\?.*v', '?v', url)

    return(avatar_url)

def find_type(page_content):

    try:
        type_elements = page_content.find('meta', {'name': 'hovercard-subject-tag'})
        type = type_elements['content']

        type = "Organization"
    except (TypeError, KeyError, AttributeError):
        type = "User"

    return type

def find_id(page_content):

    type = find_type(page_content)

    if type == 'User':
        elements = page_content.find("meta", {"name": "octolytics-dimension-user_id"})
        id_value = elements["content"]
        return int(id_value)
    else:
        elements = page_content.find("meta", {"name": "hovercard-subject-tag"})
        splits = elements["content"].split(":")
        id_value = splits[1]
        return int(id_value)

    return 1

def find_url(page_content):

    username = find_login(page_content)

    url_string = f'https://api.github.com/users/{username}'

    return url_string

def find_html_url(page_content):

    username = find_login(page_content)

    html_string = f'https://github.com/{username}'

    return html_string 

def find_name(page_content):
    
    type = find_type(page_content)

    if type == 'User':
        elements = page_content.find("span", {"class": "p-name vcard-fullname d-block overflow-hidden"})
        name = elements.text.strip()
        if (len(name) == 0):
            name = None
            
        return name
    else:
        elements = page_content.find("h1", {"class": "h2 lh-condensed"})
        name = elements.text.strip()
        return name      

def find_company(page_content):

    type = find_type(page_content)

    if type == 'User':
        try:
            elements = page_content.find("span", {"class": "p-org"})
            company = elements['title']
            return company
        except (TypeError, KeyError, AttributeError):
            return None
    else:
        return None

def find_blog(page_content):

    type = find_type(page_content)

    if type == 'User':
        try:
            elements = page_content.find("a", {"rel": "nofollow me"})
            blog = elements.text.strip()
            return blog
        except (TypeError, KeyError, AttributeError):
            return ""
    else:
        try:
            elements = page_content.find("a", {"rel": "nofollow"})
            blog = elements.text.strip()
            return blog
        except (TypeError, KeyError, AttributeError):
            return ""

def find_location(page_content):

    type = find_type(page_content)

    if type == 'User':
        try:
            elements = page_content.find("span", {"class": "p-label"})
            location = elements.text.strip()
            return location
        except (TypeError, KeyError, AttributeError):
            return None
    else:
        try:
            elements = page_content.find("span", {"itemprop": "location"})
            location = elements.text.strip()
            return location
        except (TypeError, KeyError, AttributeError):
            return None    

def find_bio(page_content):

    type = find_type(page_content)

    if type == 'User':
            elements = page_content.find("div", {"class": "p-note user-profile-bio mb-3 js-user-profile-bio f4"})
            bio = elements['data-bio-text']
            if bio != "":
                return bio
            else:
                return None
    else:
        elements = page_content.find("div", {"class": "container-xl pt-4 pt-lg-0 p-responsive clearfix"})
        specific_class = elements.find("div", {"class": "color-fg-muted"})
        bio = specific_class.text.strip()
        if bio != "":
            return bio
        else:
            return None 

def find_twitter(page_content):

    elements = page_content.findAll('a', {'rel': 'nofollow me'})

    for element in elements:
        twitter_url = element['href']
        if 'twitter' in twitter_url:
            last_slash_index = twitter_url.rfind('/')
            username = twitter_url[last_slash_index + 1:]
            return username

def find_public_repos(username):

    # elements = page_content.find("meta", {"name" : "description"})
    # string = elements['content']

    # numbers = re.findall(r'\d+', string)
    # repo_number = numbers[0]

    page = requests.get("https://github.com/search?q=" + username + "&type=users")
    payload = json.loads(page.text)["payload"]["results"][0]
    repo_number = payload["repos"]

    return repo_number

def find_followers(username):

    page = requests.get("https://github.com/search?q=" + username + "&type=users")
    payload = json.loads(page.text)["payload"]["results"][0]
    follower_value = payload["followers"]

    return follower_value

def find_following(username):

    URL = f'https://github.com/{username}'
    page = requests.get(URL)
    page_content = BeautifulSoup(page.content, "html.parser")
    type = find_type(page_content)

    if type == 'User':
        
        elements = page_content.find_all('span', class_='text-bold color-fg-default')
        try:
            following_value = elements[1].get_text()
        except:
            following_value = '0'

        if 'k' in following_value:
            number = following_value[:-1]   
            number = float(number)*1000
            min_pages =     (number / 50)
            follow_url = f'https://github.com/{username}?page={min_pages}&tab=following'
            follow_page = requests.get(follow_url)
            follow_content = BeautifulSoup(follow_page.content, "html.parser")
            next_element = follow_content.find('div', {'class', 'pagination' })

            next_element = follow_content.find('div', {'class', 'pagination' })
            try:
                next_string = next_element.find('span', {'class', 'disabled color-fg-muted'})
            except:
                next_string = None

            if next_string == None:
                follow_url = f'https://github.com/{username}?page={min_pages + 1}&tab=following'
                follow_page = requests.get(follow_url)
                follow_content = BeautifulSoup(follow_page.content, "html.parser")

                last_elements = follow_content.findAll("div", {"class" : "d-table table-fixed col-12 width-full py-4 border-bottom color-border-muted"})
                count = len(last_elements)
                following_count = number + count
                return(int(following_count))

            else: 
                follow_page = requests.get(follow_url)
                follow_content = BeautifulSoup(follow_page.content, "html.parser")

                last_elements = follow_content.findAll("div", {"class" : "d-table table-fixed col-12 width-full py-4 border-bottom color-border-muted"})
                count = len(last_elements)    
                following_count = number - count
                return(int(following_count))
            
        return int(following_value)
    else:
        following_value = 0
        return int(following_value)

def get_name_list(username):

        name_list = []

        if find_type(get_username_page(username)) == 'User':

            repos = get_repo_list(username)
            count = 0
            for name in repos:
                name = repos[count].find('h3').find('a')

                repo_name = name.text.strip()
                name_list.append(repo_name)
                count += 1

            return name_list
        else:
            repos = get_org_repo_list(username)
            count = 0
            name_list = []
            for name in repos:
                name = repos[count].find('h3').find('a')

                repo_name = name.text.strip()
                name_list.append(repo_name)
                count += 1

            return name_list

def get_id_list(name_list, username):

    count = 0
    id_list = []
    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        id = page_content.find('meta', {'name' : 'octolytics-dimension-repository_network_root_id'})
        id_list.append(id['content'])
        count += 1

    return id_list

def get_desc_list(name_list, username):

    count = 0
    desc_list = []
    for desc in name_list:
        page_content = get_repo_page(name_list[count], username)
        elements = page_content.find('title')
        try:
            string = elements.text.split(':')
            desc = string[1].strip()
        except:
            desc = None
        desc_list.append(desc)  
        count += 1

    return desc_list

def get_forked_list(name_list, username):

    count = 0
    forked_list = []
    for forked in name_list:
        page_content = get_repo_page(name_list[count], username)
        try:
            elements = page_content.find('span', {'class': 'text-small lh-condensed-ultra no-wrap mt-1'})
            check = elements.text
            forked = True
        except:
            forked = False
        forked_list.append(forked)
        count += 1

    return forked_list

def get_homepage_list(name_list, username):

    count = 0
    homepage_list = []
    for homepage in name_list:
        page_content = get_repo_page(name_list[count], username)
        try:
            elements = page_content.find('span', {'flex-auto min-width-0 css-truncate css-truncate-target width-fit'})
            homepage = elements.text.strip()
        except:
            homepage = None
        homepage_list.append(homepage)
        count += 1

    return homepage_list

def get_language_list(username):

    if find_type(get_username_page(username)) == 'User':
        count = 0
        language_list = []
        page_content = get_repo_content(username)
        repos = get_repo_list(username)
        for language in repos:
            try:
                elements = repos[count].find('span', {'itemprop': 'programmingLanguage'})
                language = elements.text.strip()
            except:
                language = None

            language_list.append(language)
            count += 1
        
        return language_list
    
    else:

        count = 0
        language_list = []
        page_content = get_org_repos(username)
        repos = get_org_repo_list(username)
        for language in repos:
            try:
                elements = repos[count].find('span', {'itemprop': 'programmingLanguage'})
                language = elements.text.strip()
            except:
                language = None

            language_list.append(language)
            count += 1
        
        return language_list


def get_forkcount_list(username):
    
    if find_type(get_username_page(username)) == 'User':
        count = 0
        forkcount_list = []
        page_content = get_repo_content(username)
        repos = get_repo_list(username)
        for forkcount in repos:
            try: 
                elements = repos[count].find('a', {'class': 'Link--muted mr-3'})
                fork_element = elements.find_next('a', {'class': 'Link--muted mr-3'})
                forkcount = fork_element.text.strip()
                forkcount = forkcount.replace(',','')
                forkcount = int(forkcount)
            except: 
                forkcount = 0

            forkcount_list.append(forkcount)
            count += 1
            
        return forkcount_list
    
    else:
        count = 0
        forkcount_list = []
        repos = get_org_repo_list(username)
        for forkcount in repos:
            try: 
                elements = repos[count].find('a', {'class': 'Link--muted mr-3'})
                fork_element = elements.find_next('a', {'class': 'Link--muted mr-3'})
                forkcount = fork_element.text.strip()
                forkcount = forkcount.replace(',','')
                forkcount = int(forkcount)
            except: 
                forkcount = 0

            forkcount_list.append(forkcount)
            count += 1
            
        return forkcount_list            

def get_stargazer_list(username):

    if find_type(get_username_page(username)) == 'User':
        count = 0
        stargazer_list = []
        page_content = get_repo_content(username)
        repos = get_repo_list(username)

        for stargazer in repos:
            try:
                elements = repos[count].find('a', {'class': 'Link--muted mr-3'})
                stargazer = elements.text.strip()
                stargazer = stargazer.replace(',','')
                stargazer = int(stargazer)
            except: 
                stargazer = 0

            stargazer_list.append(stargazer)
            count += 1

        return stargazer_list
    
    else:
        count = 0
        stargazer_list = []
        page_content = get_repo_content(username)
        repos = get_org_repo_list(username)

        for stargazer in repos:
            try:
                elements = repos[count].find('a', {'class': 'Link--muted mr-3'})
                stargazer = elements.text.strip()
                stargazer = stargazer.replace(',','')
                stargazer = int(stargazer)
            except: 
                stargazer = 0

            stargazer_list.append(stargazer)
            count += 1

        return stargazer_list        


def get_dbranch_list(name_list, username):

    count = 0
    dbranch_list = []

    for branch in name_list:
        page_content = get_repo_page(name_list[count], username)
        elements = page_content.find('summary', {'class' : 'btn css-truncate'})
        branch = elements.text.strip()

        dbranch_list.append(branch)
        count += 1

    return dbranch_list 

def get_oic_list(name_list, username):

    count = 0
    oic_list = []

    for __ in name_list:
        pulls_page = get_pulls_page(name_list[count], username)
        elements = pulls_page.find('a', {'class' : 'btn-link selected'})
        pulls = elements.text.strip()
        pulls = pulls.split()
        if len(pulls) == 2:
            pulls = pulls[0].replace(',','')
        
        issues_page = get_issues_page(name_list[count], username)
        elements = issues_page.find('a', {'class' : 'btn-link selected'})
        issues = elements.text.strip()
        issues = issues.split()
        if len(issues) == 2:
            issues = issues[0].replace(',','')

        oic = int(pulls) + int(issues)
        oic_list.append(oic)
        count += 1

    return oic_list

def get_topics_list(name_list, username):

    count = 0
    topics_list = []

    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        elements = page_content.findAll('a', {'class' : 'topic-tag topic-tag-link'})

        count1 = 0
        topics = []

        for __ in elements:
            topics.append(elements[count1].text.strip())
            count1 += 1

        count += 1
        topics_list.append(topics)

    return topics_list

def get_hasissue_list(name_list, username):

    count = 0
    hasissue_list = []

    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        check = page_content.find('a', {'id' : 'issues-tab'})

        if check == None:
            hasissues = False
        else:
            hasissues = True

        hasissue_list.append(hasissues)
        count += 1

    return hasissue_list

def get_hasprojects_list(name_list, username):

    count = 0
    hasprojects_list = []

    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        check = page_content.find('a', {'id' : 'projects-tab'})

        if check == None:
            hasprojects = False
        else:
            hasprojects = True
        
        hasprojects_list.append(hasprojects)
        count += 1
    
    return hasprojects_list

def get_hasdiscussion_list(name_list, username):

    count = 0
    hasdiscussion_list = []

    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        check = page_content.find('a', {'id' : 'discussions-tab'})

        if check == None:
            hasdiscussion = False
        else:
            hasdiscussion = True
        
        hasdiscussion_list.append(hasdiscussion)
        count += 1
    
    return hasdiscussion_list

def get_archived_list(name_list, username):
    
    count = 0
    archived_list = []

    for __ in name_list:
        page_content = get_repo_page(name_list[count], username)
        check = page_content.find('div', {'class' : 'flash flash-warn flash-full border-top-0 text-center text-bold py-2'})

        if check == None:
            archived = False
        else:
            archived = True
        
        archived_list.append(archived)
        count += 1
    
    return archived_list
        

def find_repo_url(repo_name, username):

    url = f'https://api.github.com/repos/{find_login(get_username_page(username))}/{repo_name}'

    return url

def find_repo_html(repo_name,username):

    html = f'https://github.com/{find_login(get_username_page(username))}/{repo_name}'

    return html



##Helper functions

def get_username_page(username):

    URL = f'https://github.com/{username}'
    page = requests.get(URL)
    page_content = BeautifulSoup(page.content, "html.parser")

    return page_content

def get_repo_page(repo_name, username):

    URL = f'https://github.com/{username}/{repo_name}'
    page = requests.get(URL)
    page_content = BeautifulSoup(page.content, "html.parser")

    return page_content

def get_repo_content(username):

    repo_URL = f'https://github.com/{username}?tab=repositories'
    page = requests.get(repo_URL)
    page_content = BeautifulSoup(page.content, "html.parser")

    return page_content

def get_repo_list(username):

        page_content = get_repo_content(username)
        source = page_content.findAll("li", {"class": "col-12 d-flex flex-justify-between width-full py-4 border-bottom color-border-muted public source"})
        forks = page_content.findAll("li", {"class": "col-12 d-flex flex-justify-between width-full py-4 border-bottom color-border-muted public fork"})
        archived = page_content.findAll("li", {"class": "col-12 d-flex flex-justify-between width-full py-4 border-bottom color-border-muted public source archived"})

        repos = source + forks + archived
    
        return repos

def get_pulls_page(repo_name, username):
        
        URL = f'https://github.com/{username}/{repo_name}/pulls'
        page = requests.get(URL)
        page_content = BeautifulSoup(page.content, "html.parser")

        return page_content

def get_issues_page(repo_name, username):
        
        URL = f'https://github.com/{username}/{repo_name}/issues'
        page = requests.get(URL)
        page_content = BeautifulSoup(page.content, "html.parser")

        return page_content

def get_org_repos(username):
        
        URL = f'https://github.com/orgs/{username}/repositories'
        page = requests.get(URL)
        page_content = BeautifulSoup(page.content, "html.parser")

        return page_content

def get_org_repo_list(username):

        page_content = get_org_repos(username)
        source = page_content.findAll("div", {"class": "public source d-block py-0 border-0"})
        forks = page_content.findAll("div", {"class": "public fork d-block py-0 border-0"})
        archived = page_content.findAll("div", {"class": "public source archived d-block py-0 border-0"})

        repos = source + forks + archived

        return repos
