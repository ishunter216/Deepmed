import React from 'react'
import {getUser, logout} from '../reducers/user'
import {generateUrl} from '../router'
import {wsConnect} from '../reducers/diagnosis'

export const HOME_ROUTE = 'home'
export const DIAGNOSIS_ROUTE = 'diagnosis'
export const NATIONAL_STATES_ROUTE = 'national-statistics'
export const SPECIFIC_STATES_ROUTE = 'specific-states'
export const SIMILAR_DIAGNOSES_ROUTE = 'individual-statistics'
export const CUSTOM_ANALYTICS_ROUTE = 'custom-analytics'
export const RESOURCES_ROUTE = 'resources'
export const LOGIN_ROUTE = 'login'
export const REGISTER_ROUTE = 'register'
export const LOGOUT_ROUTE = 'logout'
export const USER_ROUTE = 'user'

// The top-level (parent) route
const routes = {

  path: '',

  // Keep in mind, routes are evaluated in order
  children: [
    {
      path: '/login',
      name: `${LOGIN_ROUTE}`,
      action: require('./login').default,
    },
    {
      path: '/register',
      name: `${REGISTER_ROUTE}`,
      action: require('./register').default,
    },
    // auth required routes
    {
      path: '',
      children: [
        {
          path: '/',
          name: `${HOME_ROUTE}`,
          action: require('./home').default,
        },
        {
          path: '/diagnosis',
          name: `${DIAGNOSIS_ROUTE}`,
          action: require('./diagnosis').default,
        },
        {
          path: '/national-statistics',
          name: `${NATIONAL_STATES_ROUTE}`,
          action: require('./nationalStates').default,
        },
        {
          path: '/individual-statistics',
          name: `${SPECIFIC_STATES_ROUTE}`,
          action: require('./specificStates').default,
        },
        {
          path: '/similar-diagnoses',
          name: `${SIMILAR_DIAGNOSES_ROUTE}`,
          action: require('./similarDiagnoses').default,
        },
        {
          path: '/resources',
          name: `${RESOURCES_ROUTE}`,
          action: require('./resources').default,
        },
        {
          path: '/custom-analytics',
          name: `${CUSTOM_ANALYTICS_ROUTE}`,
          action: require('./customAnalytics').default,
        },
        {
          path: '/account',
          name: `${USER_ROUTE}`,
          action: require('./user').default,
        },
        {
          path: '/logout',
          name: `${LOGOUT_ROUTE}`,
          async action({store}) {
            await store.dispatch(logout())
            return {redirect: '/'}
          },
        },
      ],
      async action({store, next, pathname}) {
        const {loggedIn} = store.getState().user
        if (!loggedIn) {
          return {redirect: `/login?next=${pathname}`}
        }
        store.dispatch(wsConnect())
        return await next()
      },
    },
    // Wildcard routes, e.g. { path: '*', ... } (must go last)
    {
      path: '(.*)',
      action: require('./notFound').default,
    },
  ],

  async action({store, next}) {
    await store.dispatch(getUser())
    // Execute each child route until one of them return the result
    const route = await next()

    // Provide default values for title, description etc.
    route.title = `${route.title || 'DeepMed'}`
    route.description = route.description || ''

    return route
  },

}

// The error page is available by permanent url for development mode
if (__DEV__) {
  routes.children.unshift({
    path: '/error',
    action: require('./error').default,
  })
}

export default routes
