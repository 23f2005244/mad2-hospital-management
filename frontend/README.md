# frontend
celery -A app.celery worker --loglevel=info --pool=solo
celery -A app.celery beat --loglevel=info
## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
