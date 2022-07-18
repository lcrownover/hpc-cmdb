FROM node:lts-alpine

# install simple http server for serving static content
RUN npm install -g live-server

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
# COPY package*.json ./

# install project dependencies
# RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
# COPY . .

# build app for production with minification
# RUN npm run build

CMD [ "live-server", "--host=0.0.0.0", "--port=8080", "--no-browser", "--cors" ]
