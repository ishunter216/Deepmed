import {applyMiddleware, compose, createStore} from 'redux'
import thunk from 'redux-thunk'
import rootReducer from '../reducers'
import createHelpers from './createHelpers'
import socketMiddleware from './socketMiddleware'

export default function configureStore(initialState, helpersConfig, wsUrl) {
  const helpers = createHelpers(helpersConfig)
  const middleware = [
    thunk.withExtraArgument(helpers),
  ]

  if (process.env.BROWSER) {
    middleware.push(socketMiddleware(wsUrl))
  }

  let enhancer

  if (__DEV__) {
    // https://github.com/zalmoxisus/redux-devtools-extension#redux-devtools-extension
    let devToolsExtension = f => f
    if (process.env.BROWSER && window.devToolsExtension) {
      devToolsExtension = window.devToolsExtension()
    }

    enhancer = compose(
      applyMiddleware(...middleware),
      devToolsExtension,
    )
  } else {
    enhancer = applyMiddleware(...middleware)
  }

  // See https://github.com/rackt/redux/releases/tag/v3.1.0
  const store = createStore(rootReducer, initialState, enhancer)

  // Hot reload reducers (requires Webpack or Browserify HMR to be enabled)
  if (__DEV__ && module.hot) {
    module.hot.accept('../reducers', () =>
      // eslint-disable-next-line global-require
      store.replaceReducer(require('../reducers').default),
    )
  }

  return store
}
