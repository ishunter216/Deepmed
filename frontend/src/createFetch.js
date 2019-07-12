/* @flow */

type Fetch = (url: string, options: ?any) => Promise<any>;

type Options = {
  apiUrl: string,
  cookie?: string,
}

const transformFormUrlEncoded = (body) => {
  const str = []
  for (let p in body) {
    const key = encodeURIComponent(p)
    const value = encodeURIComponent(body[p])
    str.push(`${key}=${value}`)
  }
  return str.join('&')
}

const transformFormData = (body) => {
  let formDataBody = new FormData()
  Object.keys(body).forEach((key) => {
    formDataBody.append(key, body[key])
  })
  return formDataBody
}

const prepareRequestHeaders = (contentType = 'application/json', token) => {
  const headers = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  headers['Accept'] = `application/json`
  if (contentType !== 'multipart/form-data') {
    headers['Content-Type'] = contentType
  }
  return headers
}

const prepareRequestBody = (body, contentType) => {
  if (contentType === 'application/x-www-form-urlencoded') {
    return transformFormUrlEncoded(body)
  } else if (contentType === 'multipart/form-data') {
    return transformFormData(body)
  } else {
    return JSON.stringify(body)
  }
}

/**
 * Creates a wrapper function around the HTML5 Fetch API that provides
 * default arguments to fetch(...) and is intended to reduce the amount
 * of boilerplate code in the application.
 * https://developer.mozilla.org/docs/Web/API/Fetch_API/Using_Fetch
 */
function createFetch(fetch: Fetch, {apiUrl}: Options) {
  return async (url, { token, contentType, ...options }) => {
    const anotherDomainRequest = url.startsWith('http')
    options.body = prepareRequestBody(options.body, contentType)
    if (!anotherDomainRequest) {
      options.headers = prepareRequestHeaders(contentType, token)
    }
    try {
      const resp = await fetch(anotherDomainRequest ? url : `${apiUrl}${url}`, {
        ...options,
        headers: {
          ...options.headers,
        },
      })

      const responseText = await resp.text()
      if (responseText) {
        const responseBody = JSON.parse(responseText)
        return resp.ok ? options.success(responseBody) : options.failure(responseBody)
      } else {
        return resp.ok ? options.success({}) : options.failure({})
      }
    } catch (error) {
      return options.failure({error})
    }
  }
}

export default createFetch
