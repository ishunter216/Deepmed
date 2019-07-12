import path from 'path'
import express from 'express'
import bodyParser from 'body-parser'
import nodeFetch from 'node-fetch'
import React from 'react'
import ReactDOM from 'react-dom/server'
import PrettyError from 'pretty-error'
import App from './components/App'
import Html from './components/Html'
import {ErrorPageWithoutStyle} from './routes/error/ErrorPage'
import errorPageStyle from './routes/error/ErrorPage.css'
import createFetch from './createFetch'
import router from './router'
import assets from './assets.json'
import configureStore from './store/configureStore'
import {
  setConfigVars,
  setCurrentPathname, setQuery,
} from './reducers/global'
import config from './config'
import cookiesMiddleware from 'universal-cookie-express'

const app = express()

//
// Tell any CSS tooling (such as Material UI) to use all vendor prefixes if the
// user agent is not known.
// -----------------------------------------------------------------------------
global.navigator = global.navigator || {}
global.navigator.userAgent = global.navigator.userAgent || 'all'

//
// Register Node.js middleware
// -----------------------------------------------------------------------------
app.use(express.static(path.resolve(__dirname, 'public')))
app.use(cookiesMiddleware())
app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json())

//
// Register server-side rendering middleware
// -----------------------------------------------------------------------------
app.get('*', async (req, res, next) => {
  try {
    const cookies = req.universalCookies

    // Universal HTTP client
    const fetch = createFetch(nodeFetch, {
      apiUrl: `${config.api.url}/v1`,
      cookies,
    })

    const initialState = {}

    const store = configureStore(initialState, {
      fetch,
      cookies,
      // I should not use `history` on server.. but how I do redirection? follow universal-router
    })

    store.dispatch(setCurrentPathname(req.path))
    store.dispatch(setQuery(req.query))
    store.dispatch(setConfigVars({
      clientId: config.api.clientId,
      clientSecret: config.api.clientSecret,
      googleTrackingId: config.analytics.googleTrackingId,
      googleClientId: config.googleClientId,
      apiUrl: `${config.api.url}/v1`,
      apiBaseUrl: config.api.url,
      appUrl: config.appUrl,
      wsUrl: config.api.ws,
    }))

    const css = new Set()

    // Global (context) variables that can be easily accessed from any React component
    // https://facebook.github.io/react/docs/context.html
    const context = {
      // Enables critical path CSS rendering
      // https://github.com/kriasoft/isomorphic-style-loader
      insertCss: (...styles) => {
        // eslint-disable-next-line no-underscore-dangle
        styles.forEach(style => css.add(style._getCss()))
      },
      fetch,
      // You can access redux through react-redux connect
      store,
      storeSubscription: null,
    }

    const route = await router.resolve({
      ...context,
      pathname: req.path,
      query: req.query,
    })

    if (route.redirect) {
      res.redirect(route.status || 302, route.redirect)
      return
    }

    const data = {...route}
    data.children = ReactDOM.renderToString(
      <App context={context} store={store}>
        {route.component}
      </App>,
    )
    data.styles = [
      {id: 'css', cssText: [...css].join('')},
    ]
    data.scripts = [assets.vendor.js]
    if (route.chunks) {
      data.scripts.push(...route.chunks.map(chunk => assets[chunk].js))
    }
    data.scripts.push(assets.client.js)
    data.app = {
      apiUrl: `${config.api.url}/v1`,
      state: context.store.getState(),
      appUrl: config.appUrl,
      wsUrl: config.api.ws,
    }

    const html = ReactDOM.renderToStaticMarkup(<Html {...data} />)
    res.status(route.status || 200)
    res.send(`<!doctype html>${html}`)
  } catch (err) {
    next(err)
  }
})

//
// Error handling
// -----------------------------------------------------------------------------
const pe = new PrettyError()
pe.skipNodeFiles()
pe.skipPackage('express')

app.use((err, req, res, next) => { // eslint-disable-line no-unused-vars
  console.error(pe.render(err))
  const html = ReactDOM.renderToStaticMarkup(
    <Html
      title="Internal Server Error"
      description={err.message}
      styles={[{id: 'css', cssText: errorPageStyle._getCss()}]} // eslint-disable-line no-underscore-dangle
    >
    {ReactDOM.renderToString(
      <ErrorPageWithoutStyle error={err}/>
    )}
    </Html>,
  )
  res.status(err.status || 500)
  res.send(`<!doctype html>${html}`)
})

//
// Launch the server
// -----------------------------------------------------------------------------
if (!module.hot) {
  app.listen(config.port, () => {
    console.info(`The server is running at http://localhost:${config.port}/`)
  })
}

//
// Hot Module Replacement
// -----------------------------------------------------------------------------
if (module.hot) {
  app.hot = module.hot
  module.hot.accept('./router')
}

export default app
