from flask import Flask, render_template, redirect,request
#redirect: Sends user to another page, request : Gets values from URL
import requests
#Fetches data from API/internet

app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/all") #redirect all posts

@app.route("/all")
def all_posts():
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    #fetch the 100 posts then go all_post.html..user see 10 post
    posts = response.json() #json: Convert API data to Python list

    page = request.args.get("page", 1, type=int)
    #Get value from URL  ,Get the page value,1 Default value if no page in URL
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = posts[start:end]
    total_pages = len(posts) // per_page

    return render_template("all_posts.html", posts=paginated_posts, page=page, total_pages=total_pages)

@app.route("/posts/<int:id>")
def single_post(id):
    response = requests.get(f"https://jsonplaceholder.typicode.com/posts/{id}")
    post = response.json()
    return render_template("single_post.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)