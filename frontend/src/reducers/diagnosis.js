import createReducer, {RESET_STORE} from '../createReducer'
import {getToken} from './user'
import {WS_CONNECT, WS_OPEN, WS_SEND} from '../store/socketMiddleware'
import qs from 'query-string'

// ------------------------------------
// Constants
// ------------------------------------
export const GET_DIAGNOSIS_REQUEST = 'Diagnosis.GET_DIAGNOSIS_REQUEST'
export const GET_DIAGNOSIS_SUCCESS = 'Diagnosis.GET_DIAGNOSIS_SUCCESS'
export const GET_DIAGNOSIS_FAILURE = 'Diagnosis.GET_DIAGNOSIS_FAILURE'

export const GET_SIMILAR_DIAGNOSES_REQUEST = 'Diagnosis.GET_SIMILAR_DIAGNOSES_REQUEST'
export const GET_SIMILAR_DIAGNOSES_SUCCESS = 'Diagnosis.GET_SIMILAR_DIAGNOSES_SUCCESS'
export const GET_SIMILAR_DIAGNOSES_FAILURE = 'Diagnosis.GET_SIMILAR_DIAGNOSES_FAILURE'

export const GET_INDIVIDUAL_STATISTICS_REQUEST = 'Diagnosis.GET_INDIVIDUAL_STATISTICS_REQUEST'
export const GET_INDIVIDUAL_STATISTICS_SUCCESS = 'Diagnosis.GET_INDIVIDUAL_STATISTICS_SUCCESS'
export const GET_INDIVIDUAL_STATISTICS_FAILURE = 'Diagnosis.GET_INDIVIDUAL_STATISTICS_FAILURE'

export const GET_RESOURCES_REQUEST = 'Diagnosis.GET_RESOURCES_REQUEST'
export const GET_RESOURCES_SUCCESS = 'Diagnosis.GET_RESOURCES_SUCCESS'
export const GET_RESOURCES_FAILURE = 'Diagnosis.GET_RESOURCES_FAILURE'

export const GET_CUSTOM_ANALYTICS_REQUEST = 'Diagnosis.GET_CUSTOM_ANALYTICS_REQUEST'
export const GET_CUSTOM_ANALYTICS_SUCCESS = 'Diagnosis.GET_CUSTOM_ANALYTICS_SUCCESS'
export const GET_CUSTOM_ANALYTICS_FAILURE = 'Diagnosis.GET_CUSTOM_ANALYTICS_FAILURE'

export const CLEAR = 'Diagnosis.CLEAR'

const DIAGNOSIS = '/diagnosis/'
const SIMILAR_DIAGNOSES = '/similar-diagnoses/'
const INDIVIDUAL_STATISTICS = '/individual-statistics/'
const CUSTOM_ANALYTICS = '/custom-analytics/'

// ------------------------------------
// Actions
// ------------------------------------
export const wsConnect = () => (dispatch, getState) => {
  const {wsConnected} = getState().diagnosis
  if (process.env.BROWSER && !wsConnected) {
    const {token} = dispatch(getToken())
    dispatch({
      type: WS_CONNECT,
      path: DIAGNOSIS,
      query: {token},
      success: (data) => dispatch({type: GET_DIAGNOSIS_SUCCESS, data}),
      failure: () => dispatch({type: GET_DIAGNOSIS_FAILURE}),
    })
    dispatch({
      type: WS_CONNECT,
      path: SIMILAR_DIAGNOSES,
      query: {token},
      success: (data) => dispatch({type: GET_SIMILAR_DIAGNOSES_SUCCESS, data}),
      failure: () => dispatch({type: GET_SIMILAR_DIAGNOSES_FAILURE}),
    })
    dispatch({
      type: WS_CONNECT,
      path: INDIVIDUAL_STATISTICS,
      query: {token},
      success: (data) => dispatch({type: GET_INDIVIDUAL_STATISTICS_SUCCESS, data}),
      failure: () => dispatch({type: GET_INDIVIDUAL_STATISTICS_FAILURE}),
    })
    dispatch({
      type: WS_CONNECT,
      path: CUSTOM_ANALYTICS,
      query: {token},
      success: (data) => dispatch({type: GET_CUSTOM_ANALYTICS_SUCCESS, data}),
      failure: () => dispatch({type:GET_CUSTOM_ANALYTICS_FAILURE}),
    })
  }
}

export const getData = (values) => (dispatch, getState, {history}) => {
  if (process.env.BROWSER) {
    dispatch(getDiagnosis(values))
    dispatch(getSimilarDiagnoses(values))
    dispatch(getIndividualStatistics(values))
    dispatch(getResources(values))
    history.push('/diagnosis')
  }
}

export const getDiagnosis = (values) => (dispatch, getState) => {
  const {token} = dispatch(getToken())
  dispatch({type: GET_DIAGNOSIS_REQUEST, diagnosisForm: values})
  dispatch({type: WS_SEND, path: DIAGNOSIS, query: {token}, message: values})
}

export const getSimilarDiagnoses = (values) => (dispatch, getState) => {
  const {token} = dispatch(getToken())
  dispatch({type: GET_SIMILAR_DIAGNOSES_REQUEST})
  dispatch({type: WS_SEND, path: INDIVIDUAL_STATISTICS, query: {token}, message: values})
}

export const getIndividualStatistics = (values) => (dispatch, getState) => {
  const {token} = dispatch(getToken())
  dispatch({type: GET_INDIVIDUAL_STATISTICS_REQUEST})
  dispatch({type: WS_SEND, path: SIMILAR_DIAGNOSES, query: {token}, message: values})
}

export const getCustomAnalytics = (values) => (dispatch, getState) => {
  const {token} = dispatch(getToken())
  dispatch({type: GET_CUSTOM_ANALYTICS_REQUEST})
  dispatch({type: WS_SEND, path: CUSTOM_ANALYTICS, query: {token}, message: values})
}

export const getResources = (values) => (dispatch, getState, {fetch}) => {
  const {token} = dispatch(getToken())
  dispatch({type: GET_RESOURCES_REQUEST})
  return fetch(`/diagnosis/resources/?${qs.stringify(values)}`, {
    method: 'GET',
    token,
    success: (resources) => dispatch({type: GET_RESOURCES_SUCCESS, resources}),
    failure: (err) => dispatch({type: GET_RESOURCES_FAILURE})
  })
}

export const clear = () => ({type: CLEAR})

// ------------------------------------
// Reducer
// ------------------------------------
const initialState = {
  loading: false,
  diagnosisForm: {},
  diagnosis: {},
  similarDiagnoses: {},
  individualStatistics: {},
  customAnalytics: {},
  wsConnected: false,
  resources: {},
  customAnalyticsLoading: false,
}

export default createReducer(initialState, {
  [GET_DIAGNOSIS_REQUEST]: (state, {diagnosisForm}) => ({
    loading: true,
    diagnosisForm,
    diagnosis: {},
  }),
  [WS_OPEN]: (state, action) => ({
    wsConnected: true,
  }),
  [GET_DIAGNOSIS_SUCCESS]: (state, {data}) => ({
    loading: false,
    diagnosis: {
      ...state.diagnosis,
      ...data,
    },
  }),
  [GET_DIAGNOSIS_FAILURE]: (state, action) => ({
    loading: false,
  }),
  [GET_SIMILAR_DIAGNOSES_REQUEST]: (state, action) => ({
    similarDiagnoses: {},
  }),
  [GET_SIMILAR_DIAGNOSES_SUCCESS]: (state, {data}) => ({
    similarDiagnoses: {
      ...state.similarDiagnoses,
      ...data,
    },
  }),
  [GET_INDIVIDUAL_STATISTICS_REQUEST]: (state, action) => ({
    individualStatistics: {},
  }),
  [GET_INDIVIDUAL_STATISTICS_SUCCESS]: (state, {data}) => ({
    individualStatistics: {
      ...state.individualStatistics,
      ...data,
    },
  }),
  [GET_CUSTOM_ANALYTICS_REQUEST]: (state, action) => ({
    customAnalytics: {},
    customAnalyticsLoading: true,
  }),
  [GET_CUSTOM_ANALYTICS_SUCCESS]: (state, {data}) => ({
    customAnalytics: {
      ...state.customAnalytics,
      ...data,
    },
    customAnalyticsLoading: false,
  }),
  [GET_RESOURCES_SUCCESS]: (state, {resources}) => ({
    resources,
  }),
  [CLEAR]: (state, action) => RESET_STORE,
})
