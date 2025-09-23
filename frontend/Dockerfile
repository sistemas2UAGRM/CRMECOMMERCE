FROM node:24-alpine3.21

WORKDIR /usr/app/frontend

COPY package*.json .

RUN npm install -D tailwindcss && npm install

COPY . .

EXPOSE 4000

CMD ["npm", "run", "dev"]


