# Reddit Video Generator

## Setup Instructions

1. Clone this repository
2. In a powershell terminal, enter the cloned directory and execute the following:

   ```powershell
   pip install -r REQUIREMENTS.txt
   ```

3. Add the paths of your background videos to the `videos` option in `config.yaml`. You can place these videos in the `videos` directory if you like.

4. If automating video uploading (`automatic-upload.enabled: true`), follow the instructions in [this repository](https://github.com/pillargg/youtube-upload#getting-a-youtube-api-key) under the header **Getting a youtube api key**.
   If you did everything correctly, you should have downloaded a json file containing the client secrets for your youtube channel. Name this file `client_secrets.json` and place it in the cloned directory.

## Run Instructions

1. In a powershell terminal, enter the cloned directory and execute the following:

   `py main.py`
