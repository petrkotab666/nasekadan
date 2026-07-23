FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
RUN rm -rf /usr/share/nginx/html/.git /usr/share/nginx/html/.github /usr/share/nginx/html/nginx /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/docker-compose.yml
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/healthz || exit 1
