import React from 'react'
import {AppLayout} from '../../components'
import Register from './Register'
import {setCurrentRouteName} from '../../reducers/global'

function action({store, route}) {
  store.dispatch(setCurrentRouteName(route.name))

  return {
    title: 'Register',
    component: <AppLayout><Register/></AppLayout>,
  }
}

export default action
