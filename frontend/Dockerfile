FROM oven/bun:latest

WORKDIR /usr/src/app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build-only

CMD ["sh", "-c", "cp -r dist/* /shared"]
