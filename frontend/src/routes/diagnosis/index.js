import React from 'react'
import Diagnosis from './Diagnosis'
import {AppLayout} from '../../components'
import {setCurrentRouteName} from '../../reducers/global'

const title = 'Diagnosis Summary and Treatment Recommendations'

async function action({store, route}) {
  store.dispatch(setCurrentRouteName(route.name))

  return {
    title,
    component: <AppLayout title={title}><Diagnosis/></AppLayout>,
  }
}

export default action
