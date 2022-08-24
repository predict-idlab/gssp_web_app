# Speech web app

## Running the web app

### Via Python

Set first DEPLOY to `False` in the Appconfig class of [app/config.py](app/config.py)
```bash
# create a virtual environment
virtualenv -p /usr/bin/python3.8 .venv
source .venv/bin/activate

# install the required packages
pip install -r requirements.txt

# start the app
python app/main.py # the app should be accessible on localhost:8080

```
### Via Docker 

Make sure that DEPLOY is set to `True` in the Appconfig class of [app/config.py](app/config.py)

```bash
# build the image 
docker build .
# you should have an output "sucessfully built <IMAGE_ID>" on the last line

# test the image
docker run -it -p 8081:80 <IMAGE_ID>
```