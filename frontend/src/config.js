/* eslint-disable max-len */

if (process.env.BROWSER) {
  throw new Error('Do not import `config.js` from inside the client-side code.')
}

module.exports = {
  // Node.js app
  port: process.env.PORT || 3000,

  // API Gateway
  api: {
    url: process.env.API_URL || 'http://api-portal.deepmed.com/api',
    ws: process.env.WS_URL || 'ws://api-portal.deepmed.com/ws/api',
    // oauth keys
    clientId: process.env.CLIENT_ID || '4XnsRtTGMUp1TO3WCniWsl5THzLNmjcfqU5Keh5C',
    clientSecret: process.env.CLIENT_SECRET || 'ugpViM0R277iKi70ZMB9PI126gFygDkHau7Ztf11L9yuQ9c8uWIzXExhoMetgJpV1YAS9szAsjs6KmCM4IIl8Y5zFhmUDBfj07o7nUCQp2MmM66GBvn3lvSCY3z2WfPn',
  },

  appUrl: process.env.APP_URL || 'http://localhost:3000',
  googleClientId: process.env.GOOGLE_CLIENT_ID || '916189985780-4a2bv7esbslbhbnvm4nq7jnt0iflmsij.apps.googleusercontent.com',

  // Web analytics
  analytics: {
    // https://analytics.google.com/
    googleTrackingId: process.env.GOOGLE_TRACKING_ID, // UA-XXXXX-X
  },
}
