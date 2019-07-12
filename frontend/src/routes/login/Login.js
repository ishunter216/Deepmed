import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Login.scss'
import {createForm} from 'rc-form'
import {googleLogin, googleLoginFailure, login} from '../../reducers/login'
import {AutofillInput, Row, Col} from '../../components'
import GoogleLogin from 'react-google-login'

class Login extends React.Component {
  handleSubmit = (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.login(values, this.props.redirectUrl)
      }
    })
  }

  render() {
    const {loading, error, googleClientId, googleLogin, googleLoading, googleLoginFailure, redirectUrl} = this.props
    const {getFieldDecorator} = this.props.form

    return (
      <div className="container login">
        <h1 className="text-center">Login</h1>
        <div className="login-container margin-top-medium">
          <form onSubmit={this.handleSubmit}>
            {error && (
              <div className="row">
                <div className="col-sm-12">
                  <div className='alert alert-danger'>
                    {error}
                  </div>
                </div>
              </div>
            )}
            <div className="form-group">
              {getFieldDecorator('email', {
                initialValue: '',
              })(
                <AutofillInput className='form-control' placeholder='Email'/>
              )}
            </div>
            <div className="form-group">
              {getFieldDecorator('password', {
                initialValue: '',
              })(
                <AutofillInput className='form-control' type='password' placeholder='Password'/>
              )}
            </div>
            <Row type='flex' gutter={16}>
              <Col xs={24} sm={12}>
                <button
                  disabled={loading}
                  type="submit"
                  className="btn btn-primary btn-block"
                >
                  Submit
                </button>
              </Col>
              <Col xs={24} sm={12}>
                <GoogleLogin
                  fetchBasicProfile={false}
                  clientId={googleClientId}
                  scope='email'
                  onSuccess={(res) => googleLogin(res, redirectUrl)}
                  onFailure={googleLoginFailure}
                  style=''
                  className={s.googleLoginBtn}
                  disabled={googleLoading}
                >
                  Sign in with Google
                </GoogleLogin>
              </Col>
            </Row>
          </form>
        </div>
      </div>
    )
  }
}


const mapState = state => ({
  ...state.login,
  googleClientId: state.global.googleClientId,
})

const mapDispatch = {
  login,
  googleLogin,
  googleLoginFailure,
}

export default connect(mapState, mapDispatch)(createForm()(withStyles(s)(Login)))
