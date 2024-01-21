from flask import Flask, abort, render_template, request, redirect, url_for
import jinja_partials
import feedparser

feeds = {
     "https://blog.teclado.com/rss/": {"title": "The Teclado Blog", "href": "https://blog.teclado.com/rss/", "show_images": True, "entries": {}},
     "https://www.joshwcomeau.com/rss.xml": {"title": "Josh W. Comeau", "href": "https://www.joshwcomeau.com/rss.xml", "show_images": True, "entries": {}}
}

def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)

    @app.route("/")
    @app.route("/feed/<path:feed_url>")
    def render_feed(feed_url: str = None):
        # 遍历 feeds 字典的 key (url) 与 value (值)
        for url, feed_ in feeds.items():
            # 从指定的URL下载feed，并将解析后的内容存储在 parsed_feed 变量 (Python 字典) 中，以便后续使用
            parsed_feed = feedparser.parse(url)
            # 遍历 parsed_feed 中的 每一项 entry
            for entry in parsed_feed.entries:
                if entry.link not in feed_["entries"]:
                    feed_["entries"][entry.link] = {**entry, "read": False}

        # 如果 feed_url是None
        # @app.route("/")
        if feed_url is None:
            feed = list(feeds.values())[0]
        # 如果 feed_url不是None
        # @app.route("/feed/<path:feed_url>")
        else:
            feed = feeds[feed_url]

        '''  

        feeds = {
            "https://blog.teclado.com/rss/": {
            "title": "The Teclado Blog",
            "href": "https://blog.teclado.com/rss/",
            "show_images": True,
            "entries": {
            # This will be filled with entries as described below
                }
            }
            # ... more feeds can be added here
        }

        feeds 由 url 与 feeds 构成, url 为 key, feed 为 值
        '''

        ''' 
        feed = {
            "title": "The Teclado Blog",
            "href": "https://blog.teclado.com/rss/",
            "show_images": True,
            "entries": {
                # This will be filled with entries as described below
            }
        }

        feed 也是一个字典，其中entries是字典中的一个key
        '''

        ''' 
        entries = {
            "https://blog.teclado.com/post1": {
                "title": "Post 1 Title",
                "summary": "Summary of post 1",
                "published": "Date published",
                # ... other entry details
            },

            "https://blog.teclado.com/post2": {
                "title": "Post 2 Title",
                "summary": "Summary of post 2",
                "published": "Date published",
                # ... other entry details
            }

            # ... more entries can be added here
        }

        '''
        return render_template("feed.html", feed = feed, entries = feed["entries"].values(), feeds = feeds)

    @app.route("/entries/<path:feed_url>")
    def render_feed_entries(feed_url: str):

        try:
            feed = feeds[feed_url]
        except KeyError:
            abort(400)

        # ex. /entries/<path:feed_url>?page=0
        # page = 0

        # ex. /entries/<path:feed_url>?page=1
        # page = 1  
        
        # 获取当前的page
        page = int(request.args.get("page", 0))

        # 每页展示5个entry
        # ex. page = 0，那么展示第 0 个 entry
        # ex. page = 1，那么展示第 5 个 ~ 第 9 个 entry
        return render_template(
            "partials/entry_page.html",
            entries = list(feed["entries"].values())[page*5 : page * 5 + 5],
            # 当前的 url
            href=feed_url, 
            # 当前页面
            page = page,
            # 最大页数
            max_page = len(feed["entries"]) // 5
        )
    
    @app.route("/feed/<path:feed_url>/entry/<path:entry_url>")
    def read_entry(feed_url: str, entry_url: str):

        # 获取 feeds中的feed_url
        feed = feeds[feed_url]
        # 获取 feed["entries"] 中的 entry_url
        entry = feed["entries"][entry_url]
        # 更新 entry["read"] 的值为 True
        entry["read"] = True

        return redirect(entry_url)
    
    # 建立 添加 新的 feed 
    @app.route("/add_feed", methods = ["POST"])
    def add_feed():
        # 对应 <input type="text" id="url" name="url" class="bg-slate-100 p-2 mb-2"> 
        # 获取 name 属性
        feed = request.form.get("url")
        # 对应 <input type="text" id="title" name="title" class="bg-slate-100 p-2 mb-2">
        # 获取 title 属性
        title = request.form.get("title")
        # 对应 <input type="checkbox" id="showImages" name="showImage" class="bg-slate-100 p-2 mb-2">
        # 获取 showImage 属性
        show_images = request.form.get("showImages")
        feeds[feed] = {"title": title, "href": feed, "show_images": show_images, "entries": {}}

        return redirect(url_for("render_feed", feed_url = feed))
    
    # # 将新的 feed 显示在 客户端 上 
    # @app.route("/render_add_feed")
    # def render_add_feed():
    #     # 将 add_feed.html 模板文件渲染成 HTML，并将这个 HTML 发送给请求这个 Flask 路由的客户端
    #     return render_template("partials/add_feed.html")

    return app