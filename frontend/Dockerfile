FROM node:latest

RUN apt update && apt upgrade -y
RUN apt install -y npm

COPY . .

RUN npm i   

CMD [ "npm", "run", "serve" ]