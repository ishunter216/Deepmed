import createReducer, {RESET_STORE} from '../createReducer'
import {getUser} from './user'
import {PREV_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE, TOKEN_COOKIE, WEEK} from '../constants'

// ------------------------------------
// Constants
// ------------------------------------
export const LOGIN_REQUEST = 'Login.LOGIN_REQUEST'
export const LOGIN_SUCCESS = 'Login.LOGIN_SUCCESS'
export const LOGIN_FAILURE = 'Login.LOGIN_FAILURE'

export const GOOGLE_LOGIN_REQUEST = 'Login.GOOGLE_LOGIN_REQUEST'
export const GOOGLE_LOGIN_SUCCESS = 'Login.GOOGLE_LOGIN_SUCCESS'
export const GOOGLE_LOGIN_FAILURE = 'Login.GOOGLE_LOGIN_FAILURE'

export const ACTIVATE_REQUEST = 'Login.ACTIVATE_REQUEST'
export const ACTIVATE_SUCCESS = 'Login.ACTIVATE_SUCCESS'
export const ACTIVATE_FAILURE = 'Login.ACTIVATE_FAILURE'

export const CLEAR = 'Login.CLEAR'

// ------------------------------------
// Actions
// ------------------------------------
export const login = (values, redirectUrl) => (dispatch, getState, {fetch}) => {
  dispatch({type: LOGIN_REQUEST})
  const {clientId, clientSecret} = getState().global
  return fetch(`/auth/token/`, {
    method: 'POST',
    contentType: 'application/x-www-form-urlencoded',
    body: {
      username: values.email,
      password: values.password,
      grant_type: 'password',
      client_id: clientId,
      client_secret: clientSecret,
    },
    success: (res) => dispatch(loginSuccess(res, redirectUrl)),
    failure: (err) => dispatch({type: LOGIN_FAILURE, error: 'Something went wrong. Please try again.'})
  })
}

export const loginSuccess = (auth, redirectUrl = '/') => (dispatch, getState, {history, cookies}) => {
  dispatch({type: LOGIN_SUCCESS})
  cookies.set(TOKEN_COOKIE, auth.access_token, {maxAge: auth.expires_in})
  cookies.set(REFRESH_TOKEN_COOKIE, auth.refresh_token, {maxAge: WEEK})
  cookies.set(PREV_TOKEN_COOKIE, auth.access_token, {maxAge: WEEK})
  dispatch(getUser())
  if (process.env.BROWSER) {
    history.push(redirectUrl)
  }
}


export const googleLoginFailure = (err) => (dispatch, getState) => {
  dispatch({type: GOOGLE_LOGIN_FAILURE, error: (err && err.error_description) || 'Something went wrong. Please try again.'})
}

export const googleLogin = ({accessToken}, redirectUrl) => (dispatch, getState, {fetch}) => {
  const {clientId, clientSecret} = getState().global
  dispatch({type: GOOGLE_LOGIN_REQUEST})
  return fetch(`/auth/convert-token/`, {
    method: 'POST',
    contentType: 'application/x-www-form-urlencoded',
    body: {
      grant_type: 'convert_token',
      backend: 'google-oauth2',
      client_id: clientId,
      client_secret: clientSecret,
      token: accessToken,
    },
    success: (res) => {
      dispatch(loginSuccess(res, redirectUrl))
      dispatch({type: GOOGLE_LOGIN_SUCCESS})
    },
    failure: (err) => dispatch(googleLoginFailure(err))
  })
}

export const activate = (key) => (dispatch, getState, {fetch, history}) => {
  dispatch({type: ACTIVATE_REQUEST})
  return fetch(`/user/activate/`, {
    method: 'PUT',
    body: {
      key,
    },
    success: (res) => {
      dispatch({type: ACTIVATE_SUCCESS, success: 'success'})
      // to prevent redirecting on server
      if (process.env.BROWSER) {
        // TODO use route
        history.replace('/login')
      }
    },
    failure: (err) => {
      dispatch({type: ACTIVATE_FAILURE, error: 'error'})
      // to prevent redirecting on server
      if (process.env.BROWSER) {
        history.replace('/login')
      }
    },
  })
}

export const clear = () => ({type: CLEAR})

// ------------------------------------
// Reducer
// ------------------------------------
const initialState = {
  loading: false,
  googleLoading: false,
  error: null,
  success: null,
}

export default createReducer(initialState, {
  [LOGIN_REQUEST]: (state, action) => ({
    loading: true,
    success: null,
    error: null,
  }),
  [LOGIN_SUCCESS]: (state, action) => ({
    loading: false,
    error: null,
  }),
  [LOGIN_FAILURE]: (state, {error}) => ({
    loading: false,
    error,
  }),
  [ACTIVATE_REQUEST]: (state, action) => ({
    success: null,
    error: null,
  }),
  [ACTIVATE_SUCCESS]: (state, {success}) => ({
    success,
    error: null,
  }),
  [ACTIVATE_FAILURE]: (state, {error}) => ({
    success: null,
    error,
  }),
  [GOOGLE_LOGIN_REQUEST]: (state, action) => ({
    googleLoading: true,
    success: null,
    error: null,
  }),
  [GOOGLE_LOGIN_SUCCESS]: (state, action) => ({
    googleLoading: false,
    error: null,
  }),
  [GOOGLE_LOGIN_FAILURE]: (state, {error}) => ({
    googleLoading: false,
    // error,
  }),
  [CLEAR]: (state, action) => RESET_STORE,
})
