import React from 'react'
import SimilarDiagnoses from './SimilarDiagnoses'
import {AppLayout} from '../../components'
import {setCurrentRouteName} from '../../reducers/global'

async function action({store, route}) {
  store.dispatch(setCurrentRouteName(route.name))
  const {similarDiagnoses} = store.getState().diagnosis

  let title = 'Diagnoses Similar to This Diagnosis'

  if (similarDiagnoses.similar_diagnosis && similarDiagnoses.similar_diagnosis.length) {
    title = `${similarDiagnoses.similar_diagnosis.length} ${title}`
  }

  return {
    title,
    component: <AppLayout title={title}><SimilarDiagnoses/></AppLayout>,
  }
}

export default action
