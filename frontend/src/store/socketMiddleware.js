import qs from 'query-string'

// Action types to be dispatched by the user
export const WS_CONNECT = 'WS_CONNECT'
export const WS_DISCONNECT = 'WS_DISCONNECT'
export const WS_SEND = 'WS_SEND'
// Action types dispatched by the WebSocket implementation
export const WS_OPEN = 'WS_OPEN'
export const WS_CLOSED = 'WS_CLOSED'

const socketMiddleware = (wsUrl) => (() => {
  let sockets = {}

  const onOpen = (ws, store, action) => (e) => {
    // Send a handshake, or authenticate with remote end
    store.dispatch({type: WS_OPEN, path: action.path, query: action.query})
  }

  const onClose = (ws, store, action) => (e) => {
    store.dispatch({type: WS_CLOSED, path: action.path, query: action.query})
  }

  const onMessage = (ws, store, action) => (e) => {
    // Parse the JSON message received on the websocket
    const data = JSON.parse(e.data)
    if (action.success) {
      action.success(data)
    }
  }

  const onError = (ws, store, action) => (e) => {
    // TODO
    if (action.failure) {
      action.failure()
    }
  }

  const initialize = (socket, store, action) => {
    socket = new WebSocket(`${wsUrl}${action.path}?${qs.stringify(action.query)}`)
    sockets[action.path] = socket
    socket.onopen = onOpen(socket, store, action)
    socket.onclose = onClose(socket, store, action)
    socket.onmessage = onMessage(socket, store, action)
    socket.onerror = onError(socket, store, action)
  }

  const close = (socket, store, action) => {
    if (socket) {
      socket.close()
      delete sockets[action.path]
    }
  }

  let attempts = 1
  const generateInterval = (k) => Math.min(30, (Math.pow(2, k) - 1)) * 1000

  return store => next => action => {
    let socket = sockets[action.path]
    switch (action.type) {
      // User request to connect
      case WS_CONNECT:
        if (!socket) {
          initialize(socket, store, action)
        }
        next(action)
        break

      // User request to disconnect
      case WS_DISCONNECT:
        close()
        next(action)
        break

      // User request to send a message
      case WS_SEND:
        if (socket) {
          socket.send(JSON.stringify(action.message))
        } else {
          console.warn('WebSocket is closed, ignoring. Trigger a WS_CONNECT first.')
        }
        next(action)
        break

      case WS_OPEN:
        attempts = 1
        next(action)
        break

      case WS_CLOSED:
        const time = generateInterval(attempts)

        setTimeout(() => {
          // We've tried to reconnect so increment the attempts by 1
          attempts++
          initialize(store, store, action)
        }, time)
        next(action)
        break
      default:
        next(action)
    }
  }
})()

export default socketMiddleware
