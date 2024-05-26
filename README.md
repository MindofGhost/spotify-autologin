# spotify-autologin
A service that allows you to automatically log into your spotify account at set intervals

It was written exclusively for personal use and is published as is without any warranty

You will need a docker to run it.

## Usage
1. Redefine `usernames` and `passwords` arrays in docker-compose.yml
\
(The first element of `passwords` will be used as password for the first element of `usernames`, the second one is for the second one, etc...)
2. Run command `docker build -t spotify-login:latest .`
3. Run command `docker-compose up -d`

## Additional settings
You can also redefine the following variables:
1. `sleeptime` - How long (s/m/h/d) will the service wait before the next login to accounts
2. `retries` - Sometimes errors occur when logging in. The service will try different login scenarios before skipping the current login/password pair. It is not recommended to assign values outside the range 4-10 to this variable 
3. `debug` - Open the debug port to connect the chrome debugger and switch logs to debug mode. (DO NOT ENABLE THIS SETTING IF YOU DO NOT KNOW WHY IT IS NEEDED)
4. `TZ` - Your timezone. Affects the time in the logs