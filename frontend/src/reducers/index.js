import {combineReducers} from 'redux'
import user from './user'
import global from './global'
import login from './login'
import register from './register'
import home from './home'
import diagnosis from './diagnosis'

export default combineReducers({
  user,
  global,
  login,
  register,
  home,
  diagnosis,
})
