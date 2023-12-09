# Reddit Video Generator

## Setup Instructions

1. Clone this repository
2. In a powershell terminal, enter the cloned directory and execute the following:

   `pip install -r REQUIREMENTS.txt`

3. Add your own background videos into the `videos\` directory. Specify these in the `videos` option in `config.yaml`.

4. If automating video uploading (`automatic-upload.enabled: true` in `config.yaml`), follow the instructions in [this repository](https://github.com/pillargg/youtube-upload) under the header **Getting a youtube api key**.
   If you did everything write, you should have downloaded a json file containing the client secrets for your youtube channel. Name this file `client_secrets.json` and place it in the cloned directory.

## Run Instructions

1. In a powershell terminal, enter the cloned directory and execute the following:

   `py main.py`
