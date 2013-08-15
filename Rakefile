desc "compile and run the site"
task :default do
  pids = [
    spawn("jekyll serve --watch"),
    spawn("sass --watch assets/css:assets/css --style compressed"),
    spawn("coffee -b -w -o assets/js -c assets/js/*.coffee")
  ]
 
  trap "INT" do
    Process.kill "INT", *pids
    exit 1
  end
 
  loop do
    sleep 1
  end
end
