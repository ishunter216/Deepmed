import React from 'react'
import CustomAnalytics from './CustomAnalytics'
import {AppLayout} from '../../components'
import {setCurrentRouteName} from '../../reducers/global'

async function action({store, route}) {
  store.dispatch(setCurrentRouteName(route.name))

  const title = 'Custom Analytics'

  return {
    title,
    component: <AppLayout title={title}><CustomAnalytics/></AppLayout>,
  }
}

export default action
