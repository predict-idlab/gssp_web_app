# Speech web app

This branch witthholds a stripped version of the speech web-app with the following differences:

It is tailored towards *adverse childhood event* study, where participants will only
obtain 1-2 images to describe.

The identifier of this study will be held within the URL that is sent to the end-user.


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
