def Exit():
    print('按下Ctrl-C 退出程序')
    while True:
        pass


try:
    from apscheduler.schedulers.blocking import BlockingScheduler
except ImportError:
    import pip
    pip.main(['install', 'apscheduler'])
    from apscheduler.schedulers.blocking import BlockingScheduler

try:
    from Pixiv import login
except ImportError:
    print('pixiv-ImportError')
    Exit()
try:
    from discord_hooks import Webhook
except ImportError:
    print('Webhook-ImportError')
    Exit()

try:
    import numpy as np
except ImportError:
    print('numpy-ImportError')
    Exit()
import os
import json
import datetime
strmd = u"\u0042\u004f\u0054\u0020\u006d\u0061\u0064\u0065\u0020\u0062\u0079\u0020\u79d1\u6280\u72fc\u0028\u0054\u0065\u0063\u0068\u0020\u0077\u006f\u006c\u0066\u0029"
artdata = dict()

if not os.path.exists("artdata.npy"):
    np.save('artdata.npy', artdata)

with open("data.json", "r") as reader:
    data = json.loads(reader.read())


# imglink = arts.link
# imgurl = arts.image.replace('https://i.pximg.net/','https://i.pixiv.cat/')

# Pixiv 登入

pixiv = login(data['setup']['Pixiv-Username'], data['setup']['Pixiv-Password'])


def UrlReplace(Url):
    return Url.replace('https://i.pximg.net/', 'https://i.pixiv.cat/')

# 紀錄最後一個作品的ID 以便為來得知有沒有新作品


def Recordlast():
    artdata = np.load('artdata.npy').item()
    for UserList in data['Item']:
        for user in UserList['Users']:
            try:
                a = pixiv.user(user).User()
                artsID = pixiv.user(user).works()[0].id

            except Exception as e:
                continue
            artdata[user] = artsID
    np.save('artdata.npy', artdata)


def Run():
    artdata = np.load('artdata.npy').item()
    for lists in data['Item']:
        for user in lists['Users']:
            try:
                arts = pixiv.user(user).works()
                Userinfo = pixiv.user(user).User()
                if artdata[user] == arts[0]['id']:
                    continue
            except KeyError :
                pass
            except Exception as e :
                if not str(e) == "'list' object has no attribute 'id'":
                    continue
            artdata[user] = arts[0].id
            for art in arts:
                embed = Webhook(lists['WebhookURL'], color=123123)
                embed.set_author(name=Userinfo['name'], url='https://www.pixiv.net/member.php?id=' + user, icon=UrlReplace(
                    Userinfo['profile_image_urls']['px_50x50']))
                embed.set_image(UrlReplace(art.image))
                embed.set_title(title=art.title, url=art.link)
                if not art.tags == None:
                    Tag = ''
                    for tags in art.tags:
                        Tag = Tag + tags + '、'
                    embed.add_field(name='標籤(Tags)', value=Tag[:-1])
                    Tag = ''
                if not art.caption == None:
                    embed.set_desc(art.caption)
                embed.set_footer(
                    text=strmd, icon="https://i.imgur.com/UNPFf1f.jpg", ts=True)
                embed.post()
    np.save('artdata.npy', artdata)


scheduler = BlockingScheduler()

try:
    Recordlast()
    Run()
    # 偵測計時器部分 請勿調整過快 過快會對pixiv伺服器造成負擔
    scheduler.add_job(Run, 'interval', hours=0.5)
    
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass