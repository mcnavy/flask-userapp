1) git clone https://github.com/mcnavy/flask-userapp.git
2) USER/PASSWORD/DB_NAME in app.config to your data
3)If you already have Elasticsearch installed skip #3
Make sure you have openJDK 11
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update
sudo apt install elasticsearch
sudo nano /etc/elasticsearch/elasticsearch.yml
Find #network.host and change that line to network.host: localhost
save that file 

4) sudo systemctl start elasticsearch - start it
5) pip install -r requirements.txt  - to install packages

6) cd pathtoapp/flask-userapp
flask db init
flask db migrate
flask db upgrade


 