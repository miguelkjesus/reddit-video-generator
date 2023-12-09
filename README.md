# Reddit Video Generator

## Setup Instructions

1. Clone this repository
2. In a powershell terminal, enter the cloned directory and execute the following:

   `pip install -r REQUIREMENTS.txt`

## Run Instructions

1. Modify configuration in the `.\config.yaml` file.
2. Create a `.\videos` directory and add your own videos. Dont forget to specify which videos to use in the config.
3. If automating video uploading (`upload:automatic: true` in config), follow the instructions in [this repository](https://github.com/pillargg/youtube-upload) under the header **Getting a youtube api key**.
   You should end by downloading a json file containing the client secrets for your youtube channel. Name this file `client_secrets.json` and place it in the cloned directory.
4. In a powershell terminal, enter the cloned directory and execute the following:

   `py main.py`
