from flask import Flask
import requests
from bs4 import BeautifulSoup
import os
from github_scraper import find_avatar_url, find_type, find_id, find_html_url, find_url, find_name, find_company, find_blog, find_location, find_bio, find_twitter, find_public_repos, find_followers, find_following, find_login, get_name_list, get_id_list, get_username_page, get_repo_content, find_repo_html, get_desc_list, get_forked_list, find_repo_url, get_homepage_list, get_language_list, get_forkcount_list, get_stargazer_list, get_dbranch_list, get_oic_list, get_topics_list, get_hasissue_list, get_hasprojects_list, get_hasdiscussion_list, get_archived_list

app = Flask(__name__)
app.config.update({
    "JSON_SORT_KEYS" : False,
})

@app.route('/users/<username>')

def get_user(username):

    page_content = get_username_page(username)

    user = {

        'login' : find_login(page_content),
        'id' : find_id(page_content),
        'avatar_url' : find_avatar_url(username), #Payload method
        'url' : find_url(page_content),
        'html_url' : find_html_url(page_content),
        'type' : find_type(page_content),
        'name' : find_name(page_content),
        'company' : find_company(page_content),
        'blog' : find_blog(page_content),
        'location' : find_location(page_content),
        'bio' : find_bio(page_content),
        'twitter_username' : find_twitter(page_content),
        'public_repos' : find_public_repos(username), #Payload method
        'followers' : find_followers(username), #Payload method
        'following' : find_following(username) #Doesn't work for filipedeschamps(??)
        
    }

    return (user)


@app.route('/users/<username>/repos')
 
def get_repos(username):

    repos_list = []  # Create an empty list to store repository dictionaries

    name_list = get_name_list(username)
    id_list = get_id_list(name_list, username)
    desc_list = get_desc_list(name_list, username)
    forked_list = get_forked_list(name_list, username)
    homepage_list = get_homepage_list(name_list, username)
    language_list = get_language_list(username)
    forkcount_list = get_forkcount_list(username)
    stargazer_list = get_stargazer_list(username)
    dbranch_list = get_dbranch_list(name_list, username)
    oic_list = get_oic_list(name_list, username)
    topic_list = get_topics_list(name_list, username)
    hasissue_list = get_hasissue_list(name_list, username)
    hasprojects_list = get_hasprojects_list(name_list, username)
    hasdiscussion_list = get_hasdiscussion_list(name_list, username)
    archived_list = get_archived_list(name_list, username)

    for count in range(find_public_repos(username)):
        repo = {
            'id': id_list[count],
            'name': name_list[count],
            'full_name' : f'{username}/{name_list[count]}',
            'owner' : {
                'login' : find_login(get_username_page(username)),
                'id' : find_id(get_username_page(username)),
            },
            'private' : 'false',
            'html_url' : find_repo_html(name_list[count],username),
            'description' : desc_list[count],
            'fork' : forked_list[count],
            'url' : find_repo_url(name_list[count], username),
            'homepage' : homepage_list[count],
            'language' : language_list[count],
            'forks_count' : forkcount_list[count],
            'stargazers_count' : stargazer_list[count],
            'watchers_count' : stargazer_list[count],
            'default_branch' : dbranch_list[count],
            'open_issues_count' : oic_list[count],
            'topics' : topic_list[count],
            'has_issues' : hasissue_list[count],
            'has_projects' : hasprojects_list[count],
            'has_discussions' : hasdiscussion_list[count],
            'archived' : archived_list[count]
        }
        repos_list.append(repo)  # Add the repository dictionary to the list

    return repos_list


if __name__ == '__main__':
    app.run(port = (os.environ.get('GITHUB_API_PORT')))

