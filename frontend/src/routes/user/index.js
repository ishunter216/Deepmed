import React from 'react'
import {AppLayout} from '../../components'
import User from './User'
import {setCurrentRouteName} from '../../reducers/global'

function action({store, route}) {
  store.dispatch(setCurrentRouteName(route.name))

  return {
    title: 'Account',
    component: <AppLayout><User/></AppLayout>,
  }
}

export default action
