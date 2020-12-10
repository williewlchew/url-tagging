# UrlTagging Demo Requests
# Willie Chew 
# 2020

# Articles of curl command
curl --header "Content-Type: application/json" -d "{\"url\":\"https://adityasridhar.com/posts/how-to-easily-use-curl-for-http-requests\"}" http://localhost:5000/link
curl --header "Content-Type: application/json" -d "{\"url\":\"https://geekflare.com/curl-command-usage-with-example/\"}" http://localhost:5000/link
curl --header "Content-Type: application/json" -d "{\"url\":\"https://linuxize.com/post/curl-command-examples/\"}" http://localhost:5000/link

# Look for curl articles with tags
curl --header "Content-Type: application/json" -d "{\"tags\":\"curl\"}" http://localhost:5000/reccomend

# Articles on f1
curl --header "Content-Type: application/json" -d "{\"url\":\"https://www.motorsport.com/f1/news/racing-point-didnt-have-enough-spares-after-bahrain-clashes/4923611/\"}" http://localhost:5000/link
curl --header "Content-Type: application/json" -d "{\"url\":\"https://www.autoweek.com/racing/formula-1/a34916402/f1-conspiracy-theory-of-the-week-says-mercedes-sabotaged-russells-tires-on-purpose/\"}" http://localhost:5000/link
curl --header "Content-Type: application/json" -d "{\"url\":\"https://www.essentiallysports.com/f1-news-mercedes-and-red-bull-f1-react-to-valtteri-bottas-and-george-russell-changing-their-instagram-bios/\"}" http://localhost:5000/link

# Look for f1 articles with tags
curl --header "Content-Type: application/json" -d "{\"tags\":\"russell+mercedes\"}" http://localhost:5000/reccomend