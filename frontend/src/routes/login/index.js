import React from 'react'
import {AppLayout} from '../../components'
import Login from './Login'
import {setCurrentRouteName} from '../../reducers/global'

function action({query, store, route}) {
  store.dispatch(setCurrentRouteName(route.name))

  return {
    title: 'Login',
    component: (
      <AppLayout>
        <Login redirectUrl={query.next} activationKey={query.activation_key}/>
      </AppLayout>
    ),
  }
}

export default action
