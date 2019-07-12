import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './User.scss'
import {createForm} from 'rc-form'
import {Input} from '../../components'
import {updateUser} from '../../reducers/user'

class User extends React.Component {
  handleSubmit = (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.updateUser(values)
      }
    })
  }

  render() {
    const {loading, error, user} = this.props
    const {getFieldDecorator, getFieldError} = this.props.form

    return (
      <div className="container login">
        <h1 className="text-center">Account</h1>
        <div className="login-container margin-top-medium">
          {user && (
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
                {getFieldDecorator('first_name', {
                  initialValue: user.first_name,
                })(
                  <Input className='form-control' error={getFieldError('first_name')} label={'First Name'}/>
                )}
              </div>
              <div className="form-group">
                {getFieldDecorator('last_name', {
                  initialValue: user.last_name,
                })(
                  <Input className='form-control' error={getFieldError('last_name')} label={'Last Name'}/>
                )}
              </div>
              <div className="form-group">
                {getFieldDecorator('email', {
                  initialValue: user.email,
                })(
                  <Input className='form-control' error={getFieldError('email')} label={'Email'}/>
                )}
              </div>
              <button
                disabled={loading}
                type="submit"
                className="btn btn-primary btn-block"
              >
                Update
              </button>
            </form>
          )}
        </div>
      </div>
    )
  }
}


const mapState = state => ({
  ...state.user,
})

const mapDispatch = {
  updateUser,
}

export default connect(mapState, mapDispatch)(createForm()(withStyles(s)(User)))
