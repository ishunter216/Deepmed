import createReducer, {RESET_STORE} from '../createReducer'

// ------------------------------------
// Constants
// ------------------------------------
export const REGISTER_REQUEST = 'Register.REQUEST'
export const REGISTER_SUCCESS = 'Register.SUCCESS'
export const REGISTER_FAILURE = 'Register.FAILURE'

export const CLOSE_ALERT = 'Register.CLOSE_ALERT'

export const CLEAR = 'Register.CLEAR'

// ------------------------------------
// Actions
// ------------------------------------
export const register = (values) => (dispatch, getState, {fetch}) => {
  dispatch({type: REGISTER_REQUEST})
  return fetch(`/user/me/`, {
    method: 'POST',
    body: {
      first_name: values.first_name,
      last_name: values.last_name,
      email: values.email,
      password: values.password,
    },
    success: (res) => dispatch({type: REGISTER_SUCCESS, success: 'success'}),
    failure: (err) => dispatch(registerFailure(err, values))
  })
}

export const registerFailure = (errors, values) => {
  return {type: REGISTER_FAILURE, errors}
}

export const closeAlert = () => ({type: CLOSE_ALERT})

export const clear = () => ({type: CLEAR})


// ------------------------------------
// Reducer
// ------------------------------------
const initialState = {
  loading: false,
  // TODO show error in alert (not per field)
  errors: null,
  success: null,
}

export default createReducer(initialState, {
  [REGISTER_REQUEST]: (state, action) => ({
    loading: true,
    errors: null,
    success: null,
  }),
  [REGISTER_SUCCESS]: (state, {success}) => ({
    loading: false,
    success,
  }),
  [REGISTER_FAILURE]: (state, {errors}) => ({
    loading: false,
    errors,
  }),
  [CLOSE_ALERT]: (state, action) => ({
    success: null,
    errors: null,
  }),
  [CLEAR]: (state, action) => RESET_STORE
})
