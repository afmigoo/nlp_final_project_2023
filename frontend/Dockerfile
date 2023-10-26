FROM node:20.9.0-slim

RUN apt update && apt upgrade -y
RUN apt install -y npm

COPY package.json .
RUN npm i   

COPY . .

CMD [ "npm", "run", "serve" ]