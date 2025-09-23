FROM oven/bun:1.2.21-alpine

WORKDIR /usr/app/frontend

COPY bun.lock package.json .

RUN bun install

COPY . .

EXPOSE 4000

CMD ["bun", "run", "dev"]


